from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


class RegistrationForm(forms.Form):
    username = forms.CharField(label=_('Usuario'), max_length=150, widget=forms.TextInput(attrs={'autocomplete': 'username'}))
    email = forms.EmailField(label=_('Correo'), max_length=254, widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    password = forms.CharField(
        label=_('Contraseña'),
        min_length=8,
        help_text=_('Mínimo 8 caracteres. No uses contraseñas comunes ni solo números.'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )


class LoginForm(forms.Form):
    username = forms.CharField(label=_('Usuario'), max_length=150, widget=forms.TextInput(attrs={'autocomplete': 'username'}))
    password = forms.CharField(label=_('Contraseña'), widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))

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
