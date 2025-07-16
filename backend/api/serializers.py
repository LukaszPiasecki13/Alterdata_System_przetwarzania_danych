from rest_framework import serializers

from .models import Transaction
import uuid
from datetime import datetime
from decimal import Decimal


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


    def validate_transaction_id(self, value):
        _ = self._validate_uuid(value, 'transaction_id')
        return value

    def validate_customer_id(self, value):
        _ = self._validate_uuid(value, 'customer_id')
        return value
    
    def validate_product_id(self, value):
        _ = self._validate_uuid(value, 'product_id')
        return value
    
    def validate_timestamp(self, value):
        # Validation done by Django automatically
        return value
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
    
    def validate_currency(self, value):
        if len(value) != 3:
            raise serializers.ValidationError("Currency must be a 3-letter code.")
        return value.upper()  
        
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value
        
    def _validate_uuid(self, uuid_code, field_name):
        try:
            return uuid.UUID(str(uuid_code)) # Str, becasue Django automatically converts a given value to the serializer to UUID object
        except Exception as e:
            raise serializers.ValidationError(f"Invalid UUID: {e} for field {field_name}")


class CsvFileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, file):
        if not file.name.endswith('.csv'):
            raise serializers.ValidationError("File must be a CSV.")
        if file.size > 50 * 1024 * 1024:  # 50 MB limit
            raise serializers.ValidationError(f"File size must not exceed 5 MB, is {file.size} B.")
        if not file.content_type == 'text/csv':
            raise serializers.ValidationError("File must be a valid CSV file.")
        if not file:
            raise serializers.ValidationError("File cannot be empty.")
        
        return file
