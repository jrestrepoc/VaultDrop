from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from apps.users.forms import RegistrationForm, LoginForm
from apps.users.services import UserService


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.cleaned_data['user'])
        next_url = request.GET.get('next') or 'core:home'
        return redirect(next_url)
    return render(request, 'users/login.html', {'form': form})


def register_view(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            user = UserService().register(**form.cleaned_data)
        except ValueError as e:
            form.add_error(None, str(e))
        else:
            login(request, user)
            return redirect('core:home')
    return render(request, 'users/register.html', {'form': form})


@login_required
def dashboard_view(request):
    billetera = getattr(request.user, 'billetera', None)
    saldo = billetera.saldo if billetera else 0
    return HttpResponse(f"Saldo: {saldo}")
