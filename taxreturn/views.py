from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.conf import settings
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TaxReturnForm
from .models import TaxReturn
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt


def home(request):
    return render(request, 'todo/home.html')

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'That username has already been taken. Please choose a new username'})
        else:
            return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'Passwords did not match'})

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form':AuthenticationForm(), 'error':'Username and password did not match'})
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form':TaxReturnForm()})
    else:
        try:
            form = TaxReturnForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form':TaxReturnForm(), 'error':'Bad data passed in. Try again.'})

@login_required
def currenttodos(request):
    todos = TaxReturn.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todo/currenttodos.html', {'todos':todos})

@login_required
def completedtodos(request):
    todos = TaxReturn.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos':todos})

@login_required
def paidtodos(request):
    todos = TaxReturn.objects.filter(user=request.user, paymentcompleted__isnull=False).order_by('-paymentcompleted')
    return render(request, 'todo/paidtodos.html', {'todos':todos})

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(TaxReturn, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TaxReturnForm(instance=todo)
        request.session['todo_id'] = todo.id
        return render(request, 'todo/viewtodo.html', {'todo':todo, 'form':form})
    else:
        try:
            form = TaxReturnForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo':todo, 'form':form, 'error':'Bad info'})

@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(TaxReturn, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')
    
# @login_required
# #def process_payment(request, todo_pk):
# def process_payment(request, todo_pk):
#     #todo_id = request.session.get('todo_id')
#     host = request.get_host()
#     todo = get_object_or_404(TaxReturn, pk=todo_pk, user=request.user)

#     paypal_dict = {
#         'business': settings.PAYPAL_RECEIVER_EMAIL,
#         'amount': '59.99',
#         'item_name': 'Tax return {}'.format(todo.id),
#         'invoice': str(todo.id),
#         'currency_code': 'CAD',
#         'notify_url': 'http://{}{}'.format(host,
#                                         reverse('paypal-ipn')),
#         'return_url': 'http://{}{}'.format(host,
#                                             reverse('payment_done', args=(todo.id,))),
#         'cancel_return': 'http://{}{}'.format(host,
#                                                 reverse('payment_cancelled', args=(todo.id,))),
#     }
#     form = PayPalPaymentsForm(initial=paypal_dict)

#     return render(request, 'todo/process_payment.html', {'todo':todo, 'form': form})

#@csrf_exempt
def proceed_payment(request, todo_pk):
    host = request.get_host()
    todo = get_object_or_404(TaxReturn, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': '59.99',
            'item_name': 'Tax return {}'.format(todo.id),
            'invoice': str(todo.id),
            'currency_code': 'CAD',
            'notify_url': 'http://{}{}'.format(host,
                                            reverse('paypal-ipn')),
            'return_url': 'http://{}{}'.format(host,
                                             reverse('payment_done', args=(todo.id,))),
            'cancel_return': 'http://{}{}'.format(host,
                                                 reverse('payment_cancelled', args=(todo.id,))),
        }
        form = PayPalPaymentsForm(initial=paypal_dict)

        #return redirect('process_payment', todo_pk=todo)
        return render(request, 'todo/process_payment.html', {'todo':todo, 'form': form})
        
@csrf_exempt
def payment_done(request, todo_pk):
    todo = get_object_or_404(TaxReturn, pk=todo_pk, user=request.user)
    todo.paymentcompleted = timezone.now()
    todo.save()
    return render(request, 'todo/payment_done.html', {'todo': todo})

@csrf_exempt
def payment_canceled(request, todo_pk):
    todo = get_object_or_404(TaxReturn, pk=todo_pk, user=request.user)
    return render(request, 'todo/payment_cancelled.html', {'todo': todo})

@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(TaxReturn, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')
