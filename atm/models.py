from django.db import models


class Account(models.Model):
    acc_no = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return str(self.acc_no)


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    type = models.CharField(max_length=10)   # Deposit / Withdraw
    amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)


