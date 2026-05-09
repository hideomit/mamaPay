from django import forms

from users.models import Child, Request


class ChildModelForm(forms.ModelForm):
    photo = forms.ImageField(required=False)
    max_photo_size = 5 * 1024 * 1024

    class Meta:
        model = Child
        fields = ('name', 'photo')

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and photo.size > self.max_photo_size:
            raise forms.ValidationError('写真のサイズが大きすぎます。5MB以下の画像を選んでください。')
        return photo
# photo のところ not trueにしてみる

 #   name = forms.CharField(label='こどもの名前', max_length=255, required=True, widget=forms.TextInput())

class ApplyTaskForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('cuser', 'puser', 'task', 'status')
