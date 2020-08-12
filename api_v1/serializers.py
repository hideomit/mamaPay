from rest_framework import serializers

from batch.models import MonthlySummary


class MonthlySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlySummary
        fields = ['summary_ym', 'count', 'price']

