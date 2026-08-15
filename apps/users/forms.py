from django import forms


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(min_length=8, widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']
        return email
