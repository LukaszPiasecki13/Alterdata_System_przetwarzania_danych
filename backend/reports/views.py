from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated


from api.models import Transaction
from reports.lib.utils import calculate_total_amount_PLN, calculate_total_unique_field
from reports.serializers import CustomerSummarySerializer

from lib.logging_config import logger


class CustomerSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, customer_id):
        input_data_serializer = CustomerSummarySerializer(data=request.query_params)
        input_data_serializer.is_valid(raise_exception=True)
        
        try:
            start_date = input_data_serializer.validated_data.get('start_date', None)
            end_date = input_data_serializer.validated_data.get('end_date', None)

            if start_date and end_date:
                transactions = Transaction.objects.filter(customer_id=customer_id)
                transactions = transactions.filter(timestamp__gte=start_date)
                transactions = transactions.filter(timestamp__lte=end_date)

            else:
                transactions = Transaction.objects.filter(customer_id=customer_id)


            if not transactions.exists():
                logger.warning(
                    f"No transactions found for customer_id: {customer_id}")
                return Response({"error": "No transactions found for this customer."}, status=404)

            total_amount_PLN = calculate_total_amount_PLN(transactions)
            total_unique_products = calculate_total_unique_field(
                transactions, 'product_id')
            earliest_transaction = transactions.order_by('timestamp').first()

            return Response({
                "customer_id": customer_id,
                "total_amount_PLN": total_amount_PLN,
                "total_unique_products": total_unique_products,
                "earliest_transaction_date": earliest_transaction.timestamp
            })
        except Exception as e:
            logger.error(f"Error in CustomerSummaryView: {e}")
            raise e


class ProductSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, product_id):
        try:
            transactions = Transaction.objects.filter(product_id=product_id)
            if not transactions.exists():
                return Response({"error": "No transactions found for this product."}, status=404)

            total_quantity = transactions.aggregate(Sum('quantity'))[
                'quantity__sum']
            total_amount_PLN = calculate_total_amount_PLN(transactions)
            total_unique_customers = calculate_total_unique_field(
                transactions, 'customer_id')

            return Response({
                "product_id": product_id,
                "total_quantity": total_quantity,
                "total_amount_PLN": total_amount_PLN,
                "total_unique_customers": total_unique_customers

            })
        except Exception as e:
            logger.error(f"Error in ProductSummaryView: {e}")
            raise e
