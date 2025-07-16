from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum


from api.models import Transaction
from reports.lib.utils import calculate_total_amount_PLN, calculate_total_unique_field




class CustomerSummaryView(APIView):

    def get(self, request, customer_id):

        transactions = Transaction.objects.filter(customer_id = customer_id)
        if not transactions.exists():
            return Response({"error": "No transactions found for this customer."}, status=404)
        
        total_amount_PLN = calculate_total_amount_PLN(transactions)
        total_unique_products = calculate_total_unique_field(transactions, 'product_id')
        earliest_transaction= transactions.order_by('timestamp').first()

        return Response({
            "customer_id": customer_id,
            "total_amount_PLN": total_amount_PLN,
            "total_unique_products": total_unique_products,
            "earliest_transaction_date": earliest_transaction.timestamp
        })


        
class ProductSummaryView(APIView):

    def get(self, request, product_id):

        transactions = Transaction.objects.filter(product_id = product_id)
        if not transactions.exists():
            return Response({"error": "No transactions found for this product."}, status=404)
        

        total_quantity = transactions.aggregate(Sum('quantity'))['quantity__sum'] 
        total_amount_PLN = calculate_total_amount_PLN(transactions)
        total_unique_customers = calculate_total_unique_field(transactions, 'customer_id')


        return Response({
            "product_id": product_id,
            "total_quantity": total_quantity,
            "total_amount_PLN": total_amount_PLN,
            "total_unique_customers": total_unique_customers

        })
