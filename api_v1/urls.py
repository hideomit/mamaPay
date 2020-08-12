from django.conf.urls import url
from django.urls import path
from rest_framework_swagger.views import get_swagger_view

from api_v1.views import MonthlySummaryApiView

schema_view = get_swagger_view(title='api_list')


urlpatterns = [

    path('monthly_summary/', MonthlySummaryApiView.as_view()), ##エンドポイントとはurl
    url(r'^swagger/', schema_view),

]