from django.shortcuts import render, get_object_or_404

# Create your views here.
from rest_framework import views, status
from rest_framework.response import Response

from accounts.views import ApproveTaskView
from api_v1.serializers import MonthlySummarySerializer, MonthlyChildSummarySerializer, TaskSerializer, \
    TicketSerializer, RequestSerializer, HistorySerializer, TicketHoldingSerializer, ChildBalanceSerializer, \
    ChildSerializer
from batch.models import MonthlySummary, MonthlyChildSummary
from task.models import Task
from ticket.models import Ticket
from users.models import Balance, Request, History, Ticket_holding, Child


class MonthlySummaryApiView(views.APIView):
    def get_serializer(self):
        return MonthlySummarySerializer()

    def get(self, request, *args, **kwargs):
        ms = MonthlySummary.objects.all()
        serializer = MonthlySummarySerializer(instance=ms, many=True) ##複数のデータ返すときはmeny=Trueが必須
        return Response(serializer.data, status.HTTP_200_OK) ##200が正常、404がNotFound


class MonthlyChildSummaryApiView(views.APIView):
    def get_serializer(self):
        return MonthlyChildSummarySerializer()

    def get(self, request, *args, **kwargs):
#        mcs = MonthlyChildSummary.objects.select_related('cuser').all()
        mcs = MonthlyChildSummary.objects.all()

        serializer = MonthlyChildSummarySerializer(instance=mcs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class TaskCreateApiView(views.APIView):
    def get_serializer(self):
        return TaskSerializer()

    def get(self, request, *args, **kwargs):
        task_list = Task.objects.all()
        serializer = TaskSerializer(instance=task_list, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class TaskDeleteApiView(views.APIView):
    def get_serializer(self):
        return TaskSerializer() #postのinputをうまく入力する為に必要

    def delete(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, id=pk)
        task.delete()
        return Response(status.HTTP_204_NO_CONTENT) # data登録は201、参照は200　deleteはresponseなし


class TaskUpdateApiView(views.APIView):
    def get_serializer(self):
        return TaskSerializer()

    def put(self, request, pk, *args, **kwargs): #putは全項目更新、patchが指定項目の更新
        task = get_object_or_404(Task, id=pk)
        selializer = TaskSerializer(instance=task, data=request.data)
        selializer.is_valid(raise_exception=True)
        selializer.save()

        return Response(selializer.data, status.HTTP_200_OK)

    def patch(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, id=pk)
        selializer = TaskSerializer(instance=task, data=request.data, partial=True) #partial 一部のデータだけ更新
        selializer.is_valid(raise_exception=True)
        selializer.save()

        return Response(selializer.data, status.HTTP_200_OK)


class TaskDetailApiView(views.APIView):
    def get(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, id=pk)
        selializer = TaskSerializer(instance=task)

        return Response(selializer.data, status.HTTP_200_OK)


class TicketCreateApiView(views.APIView):
    def get_serializer(self):
        return TicketSerializer()

    def get(self, request, *args, **kwargs):
        task_list = Ticket.objects.all()
        serializer = TicketSerializer(instance=task_list, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = TicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class TicketUpdateApiView(views.APIView):
    def get_serializer(self):
        return TicketSerializer()

    def put(self, request, pk, *args, **kwargs): #putは全項目更新、patchが指定項目の更新
        ticket = get_object_or_404(Ticket, id=pk)
        selializer = TicketSerializer(instance=ticket, data=request.data)
        selializer.is_valid(raise_exception=True)
        selializer.save()

        return Response(selializer.data, status.HTTP_200_OK)

    def patch(self, request, pk, *args, **kwargs):
        ticket = get_object_or_404(Task, id=pk)
        selializer = TicketSerializer(instance=ticket, data=request.data, partial=True) #partial 一部のデータだけ更新
        selializer.is_valid(raise_exception=True)
        selializer.save()

        return Response(selializer.data, status.HTTP_200_OK)


class TicketDetailApiView(views.APIView):
    def get(self, request, pk, *args, **kwargs):
        ticket = get_object_or_404(Task, id=pk)
        selializer = TicketSerializer(instance=task)

        return Response(selializer.data, status.HTTP_200_OK)


class TicketDeleteApiView(views.APIView):
    def get_serializer(self):
        return TicketSerializer()

    def delete(self, request, pk, *args, **kwargs):
        ticket = get_object_or_404(Ticket, id=pk)
        ticket.delete()
        return Response(status.HTTP_204_NO_CONTENT)


class ChildBalanceGetApiView(views.APIView):
    def get_serializer(self):
        return ChildBalanceSerializer()

    def get(self, request, *args, **kwargs):
        child_id = self.kwargs['child_id']
        balance = Balance.objects.get(cuser_id=child_id)
        selializer = ChildBalanceSerializer(instance=balance)

        return Response(selializer.data, status.HTTP_200_OK)


class RequestGetApiView(views.APIView):
    def get_serializer(self):
        return RequestSerializer()

    def get(self, request, *args, **kwargs):
        child_id = self.kwargs['child_id']
        rq = Request.objects.filter(cuser=child_id)

        selializer = RequestSerializer(instance=rq, many=True)

        return Response(selializer.data, status.HTTP_200_OK)


class HistoryGetApiView(views.APIView):
    def get_serializer(self):
        return HistorySerializer()

    def get(self, request, *args, **kwargs):
        child_id = self.kwargs['child_id']
        ht = History.objects.filter(cuser=child_id)

        selializer = HistorySerializer(instance=ht, many=True)

        return Response(selializer.data, status.HTTP_200_OK)


class TicketHoldingGetApiView(views.APIView):
    def get_serializer(self):
        return TicketHoldingSerializer()

    def get(self, request, *args, **kwargs):
        child_id = self.kwargs['child_id']
        th = Ticket_holding.objects.filter(cuser=child_id)

        selializer = TicketHoldingSerializer(instance=th, many=True)

        return Response(selializer.data, status.HTTP_200_OK)


class ChildCreateApiView(views.APIView):
    def get_serializer(self):
        return ChildSerializer()

    def get(self, request, *args, **kwargs):
        child_list = Child.objects.all()
        serializer = ChildSerializer(instance=child_list, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ChildSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


#class TaskApproveApiView(views.APIView):

 #   def post(self, request, *args, **kwargs):
        #配列listを投げたい

  #      request_id_list = request.POST.getlist('approve_task_list')
  #      ApproveTaskView.task_data_save(request_id_list)

  #      return Response(status.HTTP_200_OK)