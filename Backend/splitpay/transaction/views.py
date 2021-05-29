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

#403 200


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@parser_classes([JSONParser])
def payment(request):
    data = request.data
    amount = data["amount"]
    if(amount<1):
        return Response({
                    'message': f'Amount has to be greater than 1'
                },status=403) 
    data["payer"] = request.user.id
    try:
        payee = User.objects.get(phone_number=data["payee"])
    except:
        return Response({
                    'message': f'User with the phone number {data["payee"]} does not exist'
                },status=400) 
    data["payee"] = payee.id
    serializer = TransactionSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        flag=0
        try:
            debt = Debt.objects.get(user1=request.user.id,user2=payee.id)
            debt.amount_left+=amount
            debt.save()
            print(debt.amount_left)
        except:
            flag+=1
        try:
            debt = Debt.objects.get(user1=payee.id,user2=request.user.id)
            debt.amount_left-=amount
            debt.save()
            print(debt.amount_left)
        except:
            flag+=1
        if(flag==2):
            debt_data={}
            debt_data["amount_left"]=amount
            debt_data["user1"]=request.user.id
            debt_data["user2"]=payee.id
            debt_serializer = DebtSerializer(data=debt_data)
            if debt_serializer.is_valid():
                debt_serializer.save()
            else:
                return Response({
                        'status':'failed',
                        'message':debt_serializer.errors
                    },status=401) 
        return Response({
                'message':f'{amount} payed to {payee.name}'
            },status=200)

    return Response({
                'status':'failed',
                'message':serializer.errors
            },status=402)


@api_view(['GET'])
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
    trans_data["payer"]=request.user.id
    print(amount)
    for i in data['payee']:
        try:
            user=User.objects.get(phone_number=i)
            user2.append(user)
        except:
            return Response({
                'status':'failed',
                'message':f'User with phone number {i} does not exist'
            },status=400)

    for i in user2:
        flag=0
        trans_data["payee"]=i.id
        serializer = TransactionSerializer(data=trans_data)
        if serializer.is_valid():
            serializer.save()
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
                debt_data["user1"]=request.user.id
                debt_data["user2"]=i.id
                debt_serializer = DebtSerializer(data=debt_data)
                if debt_serializer.is_valid():
                    debt_serializer.save()
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
                },status=200)


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
    trans += Transaction.objects.filter(payer=request.user.id)
    trans += Transaction.objects.filter(payee=request.user.id)
    trans = sorted(trans, key=operator.attrgetter('created_at'), reverse=True)
    serializer = TransactionSerializer(trans, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@parser_classes([JSONParser])
def splits(request):

    data={}

    active_pos = Debt.objects.filter(user1=request.user.id).exclude(amount_left=0)
    serializer = DebtSerializer(active_pos, many=True)
    data['active_pos'] = serializer.data
    active_neg = Debt.objects.filter(user2=request.user.id).exclude(amount_left=0)
    serializer = DebtSerializer(active_neg, many=True)
    data['active_neg'] = serializer.data

    all_splits_pos = Debt.objects.filter(user1=request.user.id)
    serializer = DebtSerializer(all_splits_pos, many=True)
    data['all_splits_pos'] = serializer.data
    all_splits_neg = Debt.objects.filter(user2=request.user.id)
    serializer = DebtSerializer(all_splits_neg, many=True)
    data['all_splits_neg'] = serializer.data

    money = 0
    money += Debt.objects.filter(user1=request.user.id).aggregate(Sum('amount_left'))['amount_left__sum']
    money -= Debt.objects.filter(user2=request.user.id).aggregate(Sum('amount_left'))['amount_left__sum']
    data['money'] = money # If positive then collect else pay

    return Response(data)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@parser_classes([JSONParser])
def split(request,pk):

    data = {}
    flag=0
    try:
        debt = Debt.objects.get(user1=request.user.id,user2=pk)
        money = debt.amount_left
    except:
        flag+=1
    try:
        debt = Debt.objects.get(user1=pk,user2=request.user.id)
        money = -debt.amount_left
    except:
        flag+=1

    if(flag==2):
        return Response({
                'message':f'User does not exist'
            },status=400)
    
    data['money'] = money

    trans = []
    trans += Transaction.objects.filter(payer=request.user.id,payee=pk)
    trans += Transaction.objects.filter(payer=pk,payee=request.user.id)
    trans = sorted(trans, key=operator.attrgetter('created_at'))
    serializer = TransactionSerializer(trans, many=True)
    data["transactions"] = serializer.data

    return Response(data)


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

    if(flag==2):
        return Response({
                'message':f'User does not exist'
            },status=400)

    data = {}
    data["reason"] = "Settled up"
    data["amount"] = abs(money)
    if(money>0):
        data["payer"] = pk
        data["payee"] = request.user.id
    else:
        data["payer"] = request.user.id
        data["payee"] = pk

    serializer = TransactionSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({
                    'message':f'All settled up'
                },status=200)

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