from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from celery.result import AsyncResult
from rest_framework import status


from .serializers import CsvFileSerializer, TransactionSerializer, TransactionListSerializer, TransactionDetailViewSerializer
from .models import Transaction
from .paginators import TransactionPaginator
from lib.logging_config import logger
from .tasks import process_csv_file



class TransactionUploadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            csv_file_serializer = CsvFileSerializer(data=request.data)
            csv_file_serializer.is_valid(raise_exception=True)
            file = csv_file_serializer.validated_data['file']
            file_data = file.read()

            task = process_csv_file.delay(file_data)

            return Response({
                "message": "CSV file is being processed.",
                "file_name": file.name,
                "task_id": task.id
            }, status=200)

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return Response({"error": "An error occurred while processing the file."}, status=500)

class TaskStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        result = AsyncResult(task_id)
        task_result = result.result
        
        if isinstance(task_result, Exception):
            task_result = str(task_result)

        if result.status == 'PENDING':
            task_result = None

        return Response({
            "task_id": task_id,
            "status": result.status,
            "result": task_result
        }, status=status.HTTP_200_OK)


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
