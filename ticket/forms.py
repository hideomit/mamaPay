from django import forms

from ticket.models import Ticket


class TicketForm(forms.Form):
    ticket_name = forms.CharField(label='チケット名称', max_length=255, required=True, widget=forms.TextInput())
    price = forms.IntegerField(label='価格', required=True)


class TicketModelForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('ticket_name', 'price')
        widget = {'ticket_name': forms.TextInput(), 'price': forms.NumberInput(attrs={'min': 1})}  # 数字入力の最小値
