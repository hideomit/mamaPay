from django import forms

from users.models import Child


class ChildModelForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ('name', 'photo', 'puser')

 #   name = forms.CharField(label='こどもの名前', max_length=255, required=True, widget=forms.TextInput())