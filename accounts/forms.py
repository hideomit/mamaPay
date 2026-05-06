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


class ContactForm(forms.Form):
    name = forms.CharField(label='お名前', max_length=100)
    email = forms.EmailField(label='メールアドレス')
    subject = forms.CharField(label='件名', max_length=120)
    message = forms.CharField(label='お問い合わせ内容', max_length=2000, widget=forms.Textarea)
