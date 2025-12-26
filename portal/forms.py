from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Utente')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
