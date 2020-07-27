from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import Child
from .models import Parent


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Parent
        fields = ('username', 'email')


class ChildStatusModelForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ('name', 'photo')
