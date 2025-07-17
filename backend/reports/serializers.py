from rest_framework import serializers


class CustomerSummarySerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, data):
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError(
                    "Start date cannot be after end date.")
            
        if 'start_date' not in data and 'end_date' in data or 'end_date' not in data and 'start_date' in data:
            raise serializers.ValidationError(
                "Both start date and end date must be provided together.")
        return data