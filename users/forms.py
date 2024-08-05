from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Profile
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    GENDER_CHOICES = [
        ('M', 'Laki-laki'),
        ('F', 'Perempuan'),
    ]
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)

    class Meta:
        model = User
        fields= ['first_name', 'last_name', 'username', 'email', 'password1', 'password2','gender']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', ]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


