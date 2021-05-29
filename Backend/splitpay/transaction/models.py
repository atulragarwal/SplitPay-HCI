from django.db import models
from user.models import User
import uuid


class Debt(models.Model):

    id = models.UUIDField(default=uuid.uuid4,primary_key=True)
    amount_left = models.IntegerField() # +ve means user2 has to pay user1 else vise versa
    user1 = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'User1')
    user2 = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'User2')  

    def __str__(self):
        if(abs(self.amount_left)>0):
            return f"{self.user2} owes {self.user1} {self.amount_left}."
        elif(abs(self.amount_left)<0):
            return f"{self.user1} owes {self.user2} {abs(self.amount_left)}."
        else:
            return f"{self.user2} ans {self.user1} are settled up."



class Transaction(models.Model):

    id = models.UUIDField(default=uuid.uuid4,primary_key=True) 
    amount = models.IntegerField()
    reason = models.CharField(max_length = 250)
    created_at = models.DateTimeField(auto_now=True)
    payer = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'payer')
    payee = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'payee')

    class Meta:
        ordering=['-created_at']

    def __str__(self):
        return f"{self.payer}-{self.payee}-{self.amount}"

    