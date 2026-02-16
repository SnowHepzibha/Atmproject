from django import forms
from .models import *

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['acc_no', 'name']

class AmountForm(forms.Form):
    amount = forms.IntegerField(min_value=1)











