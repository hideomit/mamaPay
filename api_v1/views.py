from django.shortcuts import render

# Create your views here.
from rest_framework import views, status
from rest_framework.response import Response

from api_v1.serializers import MonthlySummarySerializer
from batch.models import MonthlySummary


class MonthlySummaryApiView(views.APIView):
    def get(self, request, *args, **kwargs):
        ms = MonthlySummary.objects.all()
        serializer = MonthlySummarySerializer(instance=ms, many=True) ##複数のデータ返すときはmeny=Trueが必須
        return Response(serializer.data, status.HTTP_200_OK) ##200が正常、404がNotFound

