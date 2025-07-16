from django.shortcuts import render
from rest_framework.views import APIView

from .serializers import CsvFileSerializer, TransactionSerializer

import csv
import io



class TransactionView(APIView):
    def post(self, request):
        csv_file_serializer = CsvFileSerializer(data = request.data)
        csv_file_serializer.is_valid(raise_exception=True)
        file = csv_file_serializer.validated_data['file']

        # File processing and validation
        decoded_file = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded_file)) # I thought also about csv.reader(decoded_file.splitlines()), to iterate over lines 

        errors = []
        for row in csv_reader:
            transaction_serializer = TransactionSerializer(data=row)
            if transaction_serializer.is_valid():   # I am not raising exception if one of the rows is invalid
                transaction_serializer.save()
            else:
                errors.append({"row": row, 
                               "errors": transaction_serializer.errors})
                
        print(f"Errors: {errors}")  # For debugging purposes, you can log this instead

    def get(self, request):
        return render(request, 'transactions.html', {})



        
