from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from apps.users.forms import RegistrationForm
from apps.users.services import UserService


def register_view(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            user = UserService().register(**form.cleaned_data)
        except ValueError as e:
            form.add_error(None, str(e))
        else:
            login(request, user)
            return redirect('users:dashboard')
    return render(request, 'users/register.html', {'form': form})


@login_required
def dashboard_view(request):
    billetera = getattr(request.user, 'billetera', None)
    transacciones = billetera.transacciones.all().order_by('-created_at') if billetera else []
    return render(request, 'users/dashboard.html', {
        'billetera': billetera,
        'transacciones': transacciones,
    })

