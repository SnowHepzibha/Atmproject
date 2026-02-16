from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *


def home(request):
    
    return render(request, 'home.html')

def Add_account(request):

    if request.method=="POST":

        form=AccountForm(request.POST)
        if form.is_valid():
            form.save()

    return render(request,'acc_add.html')

def deposit(request):
    

    if request.method=="POST":

        acc_no=request.POST['acc_no']
        amount=int(request.POST['amount'])
        account=Account.objects.get(acc_no=acc_no)
        
        account.balance+=amount
        account.save()
    return render(request,'deposit.html')

def withdraw(request):

    if request.method=="POST":
        acc_no=request.POST['acc_no']
        amount=int(request.POST['amount'])
        account=Account.objects.get(acc_no=acc_no)
        if account.balance >= amount:

            account.balance -= amount

            account.save()
            
        else:
            return render(request,'withdraw.html',{'error':'insufficient balance'})

    return render(request,'withdraw.html')

def check_balance(request):
    if request.method=="POST":
        acc_no=request.POST['acc_no']
        account = Account.objects.get(acc_no=acc_no)
        return render(request,'balance.html',{'balance':account.balance})
    return render(request, 'balance.html')

def statement(request, acc_no):
    account = Account.objects.get(acc_no=acc_no)
    transactions = Transaction.objects.filter(account=account)

    return render(request, 'statement.html', {
        'account': account,
        'transactions': transactions
    })

def admin_login(request):
    error=""
    if request.method == "POST":
        username=request.POST['username']
        password=request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user and user.is_staff:

            login(request, user)

            return redirect('admin_page')

        else:
            error = "Invalid username or password"

    return render(request, 'admin_login.html',{'error':error})

@login_required(login_url='admin_login')

def admin_page(request):

    if not request.user.is_staff:

        return redirect('home')

    return render(request, 'admin_page.html')

def logout_view(request):

    logout(request)

    return redirect('home')

def show_account(request):

    context={

        'all_detail':Account.objects.all()
    }

    if request.method=='POST':

        form=AccountForm(request.POST)

        if form.is_valid():

            form.save()

    return render(request,'show_account.html',context)

def updatepage(request,id):

    selected_reg= Account.objects.get(id=id)

    if request.method =='POST':

        form=AccountForm(request.POST,instance=selected_reg)

        if form.is_valid():

            form.save()

        return redirect('show_account')
    else:
        form=AccountForm(instance=selected_reg)

    context={

        'register':form
    }

    return render(request,'acc_add.html',{'form': form})

def deletepage(request,id):

    selected_reg=Account.objects.get(id=id)

    selected_reg.delete()

    return redirect('show_account')


    


