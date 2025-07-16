from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .serializers import CsvFileSerializer, TransactionSerializer
from .models import Transaction
from .paginators import TransactionPaginator

import csv
import io



class TransactionUploadView(APIView):
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



class TransactionListView(ListAPIView):
    serializer_class = TransactionSerializer
    pagination_class = TransactionPaginator

    def get_queryset(self):
        queryset = Transaction.objects.all()

        customer_id = self.request.query_params.get('customer_id', None)
        product_id = self.request.query_params.get('product_id', None)

        if customer_id:
            queryset = queryset.filter(customer_id = customer_id)

        if product_id:
            queryset = queryset.filter(product_id = product_id)

        return queryset


class TransactionDetailView(RetrieveAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    def get_object(self):
        transaction_id = self.kwargs.get('transaction_id', None)
        return Transaction.objects.get(transaction_id=transaction_id)

