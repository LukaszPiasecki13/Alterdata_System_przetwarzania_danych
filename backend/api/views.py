from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from .serializers import CsvFileSerializer, TransactionSerializer, TransactionListSerializer, TransactionDetailViewSerializer
from .models import Transaction
from .paginators import TransactionPaginator
from lib.logging_config import logger

import csv
import io


class TransactionUploadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            csv_file_serializer = CsvFileSerializer(data=request.data)
            csv_file_serializer.is_valid(raise_exception=True)
            file = csv_file_serializer.validated_data['file']

            # File processing and validation
            try:
                decoded_file = file.read().decode('utf-8')
            except UnicodeDecodeError as e:
                logger.error(f"Error decoding file: {e}")
                return Response({"error": "Invalid file format. Please upload a valid CSV file."}, status=400)

            # I thought also about csv.reader(decoded_file.splitlines()), to iterate over lines
            csv_reader = csv.DictReader(io.StringIO(decoded_file))

            errors = []
            for row in csv_reader:
                transaction_serializer = TransactionSerializer(data=row)
                if transaction_serializer.is_valid():   # I am not raising exception if one of the rows is invalid
                    transaction_serializer.save()
                else:
                    errors.append({"row": row,
                                   "errors": transaction_serializer.errors})

            logger.warning(f"Errors: {errors}")
            logger.info(f"Uploaded file: {file.name}, size: {file.size} B")

            return Response({
                "message": "CSV file processed successfully.",
                "errors": errors
            }, status=200)

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return Response({"error": "An error occurred while processing the file."}, status=500)


class TransactionListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    pagination_class = TransactionPaginator

    def get_queryset(self):
        try:
            input_data_serializer = TransactionListSerializer(
                data=self.request.query_params)
            input_data_serializer.is_valid(raise_exception=True)

            queryset = Transaction.objects.all()

            customer_id = input_data_serializer.validated_data.get(
                'customer_id', None)
            product_id = input_data_serializer.validated_data.get(
                'product_id', None)

            if customer_id:
                queryset = queryset.filter(customer_id=customer_id)

            if product_id:
                queryset = queryset.filter(product_id=product_id)

            return queryset
        except Exception as e:
            logger.error(f"Error in TransactionListView: {e}")
            raise e


class TransactionDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    def get_object(self):
        try:
            input_data_serializer = TransactionDetailViewSerializer(
                data=self.kwargs)
            input_data_serializer.is_valid(raise_exception=True)

            transaction_id = input_data_serializer.validated_data.get(
                'transaction_id', None)
            return get_object_or_404(Transaction, transaction_id=transaction_id)
        except Exception as e:
            logger.error(f"Error in TransactionDetailView: {e}")
            raise e
