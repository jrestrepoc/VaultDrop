from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


class RegistrationForm(forms.Form):
    username = forms.CharField(label=_('Usuario'), max_length=150)
    email = forms.EmailField(label=_('Correo'), max_length=254)
    password = forms.CharField(label=_('Contraseña'), min_length=8, widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']
        return email


class LoginForm(forms.Form):
    username = forms.CharField(label=_('Usuario'), max_length=150)
    password = forms.CharField(label=_('Contraseña'), widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError(_('Credenciales incorrectas. Verifica tu usuario y contraseña.'))
            cleaned_data['user'] = user
        return cleaned_data
