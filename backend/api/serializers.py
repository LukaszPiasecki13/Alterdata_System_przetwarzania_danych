from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

    def validate(self, data):
        ...

class CsvFileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, file):
        if not file.name.endswith('.csv'):
            raise serializers.ValidationError("File must be a CSV.")
        if file.size > 50 * 1024 * 1024:  # 50 MB limit
            raise serializers.ValidationError("File size must not exceed 5 MB.")
        if not file.content_type == 'text/csv':
            raise serializers.ValidationError("File must be a valid CSV file.")
        if not file:
            raise serializers.ValidationError("File cannot be empty.")
        

    

        return file
