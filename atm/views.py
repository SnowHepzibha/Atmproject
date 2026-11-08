from django.shortcuts import render, redirect,get_object_or_404
from django.db import transaction
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .models import *
from .forms import *


def home(request):
    account = Account.objects.first()

    return render(request, 'home.html', {
        'account': account
    })

def Add_account(request):

    if request.method == 'POST':
        form = AccountForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('show_account')

    else:
        form = AccountForm()

    return render(request, 'acc_add.html', {'form': form})


def deposit(request, id):

    # Get the initially selected account using database ID
    account = get_object_or_404(Account, id=id)

    if request.method == "POST":

        acc_no = request.POST.get("acc_no", "").strip()
        amount_input = request.POST.get("amount", "").strip()

        # 1. Validate account number
        if not acc_no:
            return render(request, "deposit.html", {
                "account": account,
                "error": "Please enter your account number."
            })

        # 2. Find account using entered account number
        try:
            deposit_account = Account.objects.get(acc_no=acc_no)

        except (Account.DoesNotExist, ValueError):
            return render(request, "deposit.html", {
                "account": account,
                "error": "Account does not exist! Please check your account number."
            })

        # 3. Validate deposit amount
        try:
            amount = Decimal(amount_input)

            if not amount.is_finite():
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            return render(request, "deposit.html", {
                "account": deposit_account,
                "error": "Please enter a valid deposit amount."
            })

        # 4. Check positive amount
        if amount <= 0:
            return render(request, "deposit.html", {
                "account": deposit_account,
                "error": "Deposit amount must be greater than ₹0."
            })

        # 5. Allow whole rupee amounts only
        if amount != amount.to_integral_value():
            return render(request, "deposit.html", {
                "account": deposit_account,
                "error": "Please enter a whole rupee amount."
            })

        # 6. Update balance and save transaction
        amount = int(amount)

        with transaction.atomic():

            deposit_account = Account.objects.select_for_update().get(
                id=deposit_account.id
            )

            deposit_account.balance += amount

            deposit_account.save(update_fields=["balance"])

            Transaction.objects.create(
                account=deposit_account,
                type="Deposit",
                amount=amount
            )

        # 7. Display success message
        return render(request, "deposit.html", {
            "account": deposit_account,
            "success": (
                f"Deposit Successful! ₹{amount} has been deposited. "
                f"Your current balance is ₹{deposit_account.balance}."
            )
        })

    return render(request, "deposit.html", {
        "account": account
    })


def withdraw(request, id):

    # Get the account initially using URL ID
    account = get_object_or_404(Account, id=id)

    if request.method == "POST":

        acc_no = request.POST.get("acc_no", "").strip()
        amount_input = request.POST.get("amount", "").strip()

        # Validate account number
        if not acc_no:
            return render(request, "withdraw.html", {
                "account": account,
                "error": "Please enter your account number."
            })

        # Account number must contain digits only
        if not acc_no.isdigit():
            return render(request, "withdraw.html", {
                "account": account,
                "error": "Please enter a valid account number."
            })

        # Find account using entered account number
        try:
            account = Account.objects.get(acc_no=int(acc_no))

        except Account.DoesNotExist:
            return render(request, "withdraw.html", {
                "account": get_object_or_404(Account, id=id),
                "error": "Account not found! Please check your account number."
            })

        # Validate withdrawal amount
        try:
            amount = Decimal(amount_input)

            if not amount.is_finite():
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            return render(request, "withdraw.html", {
                "account": account,
                "error": "Please enter a valid withdrawal amount."
            })

        # Minimum withdrawal amount
        if amount < Decimal("100"):
            return render(request, "withdraw.html", {
                "account": account,
                "error": "Minimum withdrawal amount is ₹100."
            })

        # Whole rupees only
        if amount != amount.to_integral_value():
            return render(request, "withdraw.html", {
                "account": account,
                "error": "Please enter a whole rupee amount."
            })

        balance = Decimal(str(account.balance))

        # Check available balance
        if amount > balance:
            return render(request, "withdraw.html", {
                "account": account,
                "error": f"Insufficient balance! Available balance is ₹{balance:.2f}."
            })

        remaining_balance = balance - amount

        # Maintain minimum balance
        if remaining_balance < Decimal("100"):
            return render(request, "withdraw.html", {
                "account": account,
                "error": "You must maintain a minimum balance of ₹100."
            })

        # Update account balance
        account.balance = int(remaining_balance)
        account.save(update_fields=["balance"])

        # Save transaction
        Transaction.objects.create(
            account=account,
            type="Withdraw",
            amount=int(amount)
        )

        # Success message
        return render(request, "withdraw.html", {
            "account": account,
            "success": (
                f"Withdrawal Successful! ₹{amount:.2f} withdrawn successfully. "
            )
        })

    return render(request, "withdraw.html", {
        "account": account
    })

def check_balance(request, id=None):

    account = None
    balance = None
    error = None

    # Get account using URL ID, if available
    if id is not None:
        account = get_object_or_404(Account, id=id)

    if request.method == "POST":

        acc_no = request.POST.get('acc_no', '').strip()

        if not acc_no:
            error = "Please enter your account number."

        else:
            try:
                entered_account = Account.objects.get(acc_no=acc_no)

                # Verify account number matches the URL account
                if account and entered_account.id != account.id:
                    error = "Account number does not match!"

                else:
                    account = entered_account
                    balance = account.balance

            except Account.DoesNotExist:
                error = "Account not found! Please enter a valid account number."

    return render(request, 'balance.html', {
        'account': account,
        'balance': balance,
        'error': error
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


def admin_required(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(admin_required, login_url='admin_login')
def show_account(request):
    accounts = Account.objects.all()

    context = {
        'accounts': accounts
    }

    return render(request, 'show_account.html', context)


def statement(request):
    account = None
    transactions = []
    error = None
    acc_no = ""

    if request.method == "POST":
        acc_no = request.POST.get("acc_no", "").strip()

        try:
            account = Account.objects.get(acc_no=acc_no)

            transactions = Transaction.objects.filter(
                account=account
            ).order_by("-date")[:10]

        except (Account.DoesNotExist, ValueError):
            error = "Account does not exist. Please check your account number."

    return render(request, "mini_statement.html", {
        "account": account,
        "transactions": transactions,
        "error": error,
        "acc_no": acc_no
    })

def updatepage(request, id):

    account = Account.objects.get(id=id)

    if request.method == 'POST':

        form = AccountForm(request.POST, instance=account)

        if form.is_valid():

            form.save()

            messages.success(request, "Account updated successfully!")

            return redirect('show_account')

    else:

        form = AccountForm(instance=account)

    return render(request, 'acc_add.html', {
        'form': form,
        'account': account
    })


def deletepage(request, id):

    account = Account.objects.get(id=id)

    if request.method == 'POST':

        account.delete()

        messages.success(request, "Account deleted successfully!")

    return redirect('show_account')