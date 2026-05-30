from django import forms

from users.models import Child, Request, TitleRank


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


class TitleRankForm(forms.ModelForm):
    class Meta:
        model = TitleRank
        fields = ('title', 'required_total_coin')
        labels = {
            'title': '称号名',
            'required_total_coin': '必要累計コイン数',
        }
        widgets = {
            'required_total_coin': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, puser, *args, **kwargs):
        self.puser = puser
        super().__init__(*args, **kwargs)

    def clean_required_total_coin(self):
        required_total_coin = self.cleaned_data['required_total_coin']
        queryset = TitleRank.objects.filter(
            puser=self.puser,
            required_total_coin=required_total_coin,
            is_active=True,
            delete_flg=False,
        )
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError('同じ必要累計コイン数の称号がすでにあります。')
        return required_total_coin
