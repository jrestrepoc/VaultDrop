from django import forms
from django.contrib.auth import authenticate


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(min_length=8, widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']
        return email


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError('Credenciales incorrectas. Verifica tu usuario y contraseña.')
            cleaned_data['user'] = user
        return cleaned_data
