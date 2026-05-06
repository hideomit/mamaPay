from django import forms
from django.contrib.auth.password_validation import validate_password
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


class EmailChangeForm(forms.Form):
    email = forms.EmailField(label='新しいメールアドレス')
    email_confirm = forms.EmailField(label='新しいメールアドレス（確認）')
    password = forms.CharField(label='現在のパスワード', widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError('現在のパスワードが正しくありません。')
        return password

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        email_confirm = cleaned_data.get('email_confirm')

        if email and email_confirm and email != email_confirm:
            raise forms.ValidationError('メールアドレスが一致しません。')

        if email and email == self.user.email:
            raise forms.ValidationError('現在と異なるメールアドレスを入力してください。')

        if email and LoginUsers.objects.exclude(pk=self.user.pk).filter(email=email).exists():
            raise forms.ValidationError('このメールアドレスはすでに使われています。')

        return cleaned_data


class ChildPasswordChangeForm(forms.Form):
    password1 = forms.CharField(label='新しいパスワード', widget=forms.PasswordInput)
    password2 = forms.CharField(label='新しいパスワード（確認）', widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password1(self):
        password = self.cleaned_data['password1']
        validate_password(password, self.user)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('パスワードが一致しません。')

        return cleaned_data
