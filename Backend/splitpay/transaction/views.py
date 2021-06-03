from django.shortcuts import render
from .models import(
    Debt,
    Transaction
)
from user.models import(
    User
)
from .serializers import(
    DebtSerializer,
    TransactionSerializer
)

from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from django.db.models import Sum
import operator

# Create your views here.

#404 201


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
@parser_classes([JSONParser])
def payment(request):

    data = request.data
    amount = data["amount"]
    if(amount<1):
        return Response({
                    'message': f'Amount has to be greater than 1'
                },status=403)

    try:
        payee = User.objects.get(phone_number=data["payee"])
    except:
        return Response({
                    'message': f'User with the phone number {data["payee"]} does not exist'
                },status=400)

    if(payee.id== request.user.id):
        return Response({
                    'message': f'You cannot pay to yourself'
                },status=404)

    serializer = TransactionSerializer(data=data)
    if serializer.is_valid():
        serializer.save(payer=request.user,payee=payee)
        flag=0
        try:
            debt = Debt.objects.get(user1=request.user.id,user2=payee.id)
            debt.amount_left+=amount
            debt.save()
        except:
            flag+=1
        try:
            debt = Debt.objects.get(user1=payee.id,user2=request.user.id)
            debt.amount_left-=amount
            debt.save()
        except:
            flag+=1
        if(flag==2):
            debt_data={}
            debt_data["amount_left"]=amount
            # debt_data["user1"]=request.user.id
            # debt_data["user2"]=payee.id
            debt_serializer = DebtSerializer(data=debt_data)
            if debt_serializer.is_valid():
                debt_serializer.save(user1=request.user,user2=payee)
            else:
                return Response({
                        'status':'failed',
                        'message':debt_serializer.errors
                    },status=401) 
        return Response({
                'message':f'{amount} payed to {payee.name}'
            },status=201)

    return Response({
                'status':'failed',
                'message':serializer.errors
            },status=402)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
@parser_classes([JSONParser])
def splitpayment(request):
    
    data = request.data
    user2 = []
    trans_data={}
    amount=round(data['amount']/(len(data['payee'])+1))
    if(amount<1):
        return Response({
                    'message': f'Amount has to be greater than 1'
                },status=403) 
    trans_data["amount"]=amount
    trans_data["reason"]=data["reason"]
    # trans_data["payer"]=request.user.id

    for i in data['payee']:
        try:
            user=User.objects.get(phone_number=i)
            user2.append(user)
            if(user.id== request.user.id):
                return Response({
                            'message': f'You cannot split with yourself twice'
                        },status=404)
        except:
            return Response({
                'status':'failed',
                'message':f'User with phone number {i} does not exist'
            },status=400)

    for i in user2:
        flag=0
        # trans_data["payee"]=i.id
        serializer = TransactionSerializer(data=trans_data)
        if serializer.is_valid():
            serializer.save(payer=request.user,payee=i)
            try:
                debt = Debt.objects.get(user1=request.user.id,user2=i.id)
                debt.amount_left+=amount
                debt.save()
            except:
                flag+=1
            try:
                debt = Debt.objects.get(user1=i.id,user2=request.user.id)
                debt.amount_left-=amount
                debt.save()
            except:
                flag+=1
            if(flag==2):
                debt_data={}
                debt_data["amount_left"]=amount
                # debt_data["user1"]=request.user.id
                # debt_data["user2"]=i.id
                debt_serializer = DebtSerializer(data=debt_data)
                if debt_serializer.is_valid():
                    debt_serializer.save(user1=request.user,user2=i)
                else:
                    return Response({
                            'status':'failed',
                            'message':debt_serializer.errors
                        },status=401)   
        else:
            return Response({
                    'status':'failed',
                    'message':serializer.errors
                },status=402)
    return Response({
                    'status':'Payment complete',
                    'message':f'{data["amount"]} split'
                },status=201)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@parser_classes([JSONParser])
def frequentcontacts(request):

    pass


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@parser_classes([JSONParser])
def recenttransaction(request):

    trans = []
    trans += Transaction.objects.filter(payer=request.user)
    trans += Transaction.objects.filter(payee=request.user)
    trans = sorted(trans, key=operator.attrgetter('created_at'), reverse=True)
    serializer = TransactionSerializer(trans, many=True)
    data = []
    for i in serializer.data:
        if(i["payer"]["id"]==request.user.id):
            temp = {
                "amount": i["amount"],
                "username": i["payee"]["name"],
                "profile_pic": i["payee"]["profile_pic"]
            }
        else:
            temp = {
                "amount": -i["amount"],
                "username": i["payer"]["name"],  
                "profile_pic": i["payer"]["profile_pic"] 
            }
        data.append(temp)

    resp = {
        "recentTrans": data
    }
    return Response(resp,status=200)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@parser_classes([JSONParser])
def splits(request):

    money = 0
    active_splits = []
    active_pos = Debt.objects.filter(user1=request.user).exclude(amount_left=0)
    serializer = DebtSerializer(active_pos, many=True)
    for i in serializer.data:
        temp={
            "amount": i["amount_left"],
            "username": i["user2"]["name"],
            "userid": i["user2"]["id"],
            "profile_pic": i["user2"]["profile_pic"]
        }
        active_splits.append(temp)
        money += i["amount_left"]

    active_neg = Debt.objects.filter(user2=request.user).exclude(amount_left=0)
    serializer = DebtSerializer(active_neg, many=True)
    for i in serializer.data:
        temp={
            "amount": -i["amount_left"],
            "username": i["user2"]["name"],
            "userid": i["user2"]["id"],
            "profile_pic": i["user2"]["profile_pic"]
        }
        active_splits.append(temp)
        money -= i["amount_left"]

    all_splits = []
    all_splits_pos = Debt.objects.filter(user1=request.user)
    serializer = DebtSerializer(all_splits_pos, many=True)
    for i in serializer.data:
        temp={
            "amount": i["amount_left"],
            "username": i["user2"]["name"],
            "userid": i["user2"]["id"],
            "profile_pic": i["user2"]["profile_pic"]
        }
        all_splits.append(temp)

    all_splits_neg = Debt.objects.filter(user2=request.user)
    serializer = DebtSerializer(all_splits_neg, many=True)
    for i in serializer.data:
        temp={
            "amount": -i["amount_left"],
            "username": i["user2"]["name"],
            "userid": i["user2"]["id"],
            "profile_pic": i["user2"]["profile_pic"]
        }
        all_splits.append(temp)

    resp ={
        "money": money, # If positive then collect else pay
        "active_splits": active_splits,
        "all_splits": all_splits
    }
    return Response(resp, status=200)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@parser_classes([JSONParser])
def split(request,pk):

    data = {}      
    flag=0
    user_det={}
    try:
        user2 = User.objects.get(id=pk)
    except:
        return Response({
                'message':f'This user does not exists'
            },status=400)
    try:
        debt = Debt.objects.get(user1=request.user,user2=user2)
        money = debt.amount_left
    except:
        flag+=1
    try:
        debt = Debt.objects.get(user1=user2,user2=request.user)
        money = -debt.amount_left
    except:
        flag+=1

    if(flag==2):
        return Response({
                'message':f'You have no transaction history with this user'
            },status=400)
    
    data['money'] = money

    trans = []
    trans += Transaction.objects.filter(payer=request.user.id,payee=pk)
    trans += Transaction.objects.filter(payer=pk,payee=request.user.id)
    trans = sorted(trans, key=operator.attrgetter('created_at'))
    serializer = TransactionSerializer(trans, many=True)
    trans = []
    for i in serializer.data:
        if(i["payer"]["id"]==request.user.id):
            temp={
                "head": "You paid",
                "amount": i["amount"],
                "reason": i["reason"]
            }
        else:
            temp={
                "head": "Paid you",
                "amount": i["amount"],
                "reason": i["reason"]
            }
        trans.append(temp)

    data["transactions"] = trans

    for i in serializer.data:
        if(i["payer"]["id"]==request.user.id):
            user_det["name"] = i["payee"]["name"]
            user_det["profile_pic"] = i["payee"]["profile_pic"]
        else:
            user_det["name"] = i["payer"]["name"]
            user_det["profile_pic"] = i["payer"]["profile_pic"]
        break
        
    data["user"] = user_det

    return Response(data,status=200)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@parser_classes([JSONParser])
def settleup(request,pk):

    flag=0
    try:
        debt = Debt.objects.get(user1=request.user.id,user2=pk)
        money = debt.amount_left
        debt.amount_left = 0
        debt.save()
    except:
        flag+=1
    try:
        debt = Debt.objects.get(user1=pk,user2=request.user.id)
        money = -debt.amount_left
        debt.amount_left = 0
        debt.save()
    except:
        flag+=1

    if(flag==2 or money==0):
        return Response({
                'message': 'You have nothing to settle up with this user'
            },status=400)
    
    try:
        user2 = User.objects.get(id=pk)
    except:
        return Response({
                'message': 'User does not exist'
            },status=400)

    data = {}
    data["reason"] = "Settled up"
    data["amount"] = abs(money)
    
    serializer = TransactionSerializer(data=data)
    if serializer.is_valid():
        if(money>0):
            serializer.save(payer=user2,payee=request.user)
        else:
            serializer.save(payer=request.user,payee=user2)
        
        return Response({
                    'message':f'All settled up with {user2.name}'
                },status=201)

    return Response({
                'status':'failed',
                'message':serializer.errors
            },status=402)
    
    



# Checking

@api_view(['GET'])
@parser_classes([JSONParser])
def allpayment(request):
    trans = Transaction.objects.all()
    serializer = TransactionSerializer(trans, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@parser_classes([JSONParser])
def alldebt(request):
    debt = Debt.objects.all()
    serializer = DebtSerializer(debt, many=True)
    return Response(serializer.data)