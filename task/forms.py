from django import forms

from task.models import Task


class TaskForm(forms.Form):
    task_name = forms.CharField(label='タスク名称', max_length=255, required=True, widget=forms.TextInput())
    price = forms.IntegerField(label='価格', required=True)



class Task2Form(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('task_name', 'price')
        widget = {'task_name': forms.TextInput(), 'price': forms.NumberInput(attrs={'min': 1})} #数字入力の最小値