from django import forms

from users.models import Child, Request


class ChildModelForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ('name', 'photo')
# photo のところ not trueにしてみる

 #   name = forms.CharField(label='こどもの名前', max_length=255, required=True, widget=forms.TextInput())

class ApplyTaskForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('cuser', 'puser', 'task', 'status')