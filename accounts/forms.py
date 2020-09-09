from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import LoginUsers
from users.models import Child


class SignupParentForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = LoginUsers
        fields = ('username', 'email')


class SignupChildForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = LoginUsers
        fields = ('username', 'email')


class ChildStatusModelForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ('name', 'photo')
