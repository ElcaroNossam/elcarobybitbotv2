from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'id': 'id_email',
            'name': 'email',
            'autocomplete': 'email'
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={
                'id': 'id_username',
                'name': 'username',
                'autocomplete': 'username'
            }),
            'password1': forms.PasswordInput(attrs={
                'id': 'id_password1',
                'name': 'password1',
                'autocomplete': 'new-password'
            }),
            'password2': forms.PasswordInput(attrs={
                'id': 'id_password2',
                'name': 'password2',
                'autocomplete': 'new-password'
            }),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'id': 'id_username', 'name': 'username', 'autocomplete': 'username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'id_password', 'name': 'password', 'autocomplete': 'current-password'})
    )


