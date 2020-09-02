from rest_framework import serializers

from batch.models import MonthlySummary, MonthlyChildSummary
from task.models import Task
from ticket.models import Ticket
from users.models import Balance, Request, History, Ticket_holding, Child


class MonthlySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlySummary
        fields = ['summary_ym', 'count', 'price']


class MonthlyChildSummarySerializer(serializers.ModelSerializer):

    cuser_name = serializers.ReadOnlyField(source='cuser.name')

    class Meta:
        model = MonthlyChildSummary
        fields = ['summary_ym', 'cuser_id', 'count', 'price', 'cuser_name']


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ['task_name', 'price']


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ['ticket_name', 'price']


class ChildBalanceSerializer(serializers.ModelSerializer):
    cuser_name = serializers.ReadOnlyField(source='cuser.name')

    class Meta:
        model = Balance
        fields = ['cuser_id', 'balance', 'cuser_name']


class RequestSerializer(serializers.ModelSerializer):
    cuser_name = serializers.ReadOnlyField(source='cuser.name')
    task_name = serializers.ReadOnlyField(source='task.task_name')

    class Meta:
        model = Request
        fields = ['id', 'cuser', 'puser', 'task', 'status', 'cuser_name', 'task_name']


class HistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = History
        fields = ['ymd', 'cuser', 'task', 'ticket', 'amount', 'ticket_holding', 'kind']


class TicketHoldingSerializer(serializers.ModelSerializer):
    cuser_name = serializers.ReadOnlyField(source='cuser.name')
    ticket_name = serializers.ReadOnlyField(source='ticket.ticket_name')

    class Meta:
        model = Ticket_holding
        fields = ['cuser', 'ticket', 'used_flg', 'cuser_name', 'ticket_name']


class ChildSerializer(serializers.ModelSerializer):

    class Meta:
        model = Child
        fields = ['id', 'puser', 'name', 'photo']


class TaskApproveSerializer(serializers.Serializer):

    request_id_list = serializers.ListField(label='承認IDリスト')

