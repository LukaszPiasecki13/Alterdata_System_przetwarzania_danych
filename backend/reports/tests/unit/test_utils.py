import pytest
from uuid import uuid4
from decimal import Decimal

from reports.tests.TransactionFactory import TransactionFactory
from api.models import Transaction
from reports.lib.constants import EXCHANGE_RATES
from reports.lib.utils import calculate_total_amount_PLN, calculate_total_unique_field

LOOP_COUNT = 25


@pytest.mark.django_db
class TestViewsAuxiliaryMethods:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        factory = TransactionFactory()
        self.backup_data = []

        for _ in range(LOOP_COUNT):
            transaction_data = factory.generate_transaction_data(
                allow_duplicates=True)
            _ = Transaction.objects.create(**transaction_data)
            self.backup_data.append(transaction_data)

    def test__calculate_total_amount_PLN(self):

        for backup_transaction in self.backup_data:

            transaction_per_customer = [
                transactions for transactions in self.backup_data if transactions['customer_id'] == backup_transaction['customer_id']]
            transactions = Transaction.objects.filter(
                customer_id=backup_transaction['customer_id'])

            total_amount_PLN = calculate_total_amount_PLN(
                transactions)

            expected_total = Decimal(0)
            for transaction in transaction_per_customer:

                rate = EXCHANGE_RATES.get(transaction['currency'])
                expected_total += Decimal(transaction['amount']
                                          ) * Decimal(rate)

            assert round(total_amount_PLN, 2) == round(expected_total, 2)

    def test__calculate_total_unique_products(self):

        for backup_transaction in self.backup_data:
            transaction_per_product = [
                transactions for transactions in self.backup_data if transactions['customer_id'] == backup_transaction['customer_id']]
            transactions = Transaction.objects.filter(
                customer_id=backup_transaction['customer_id'])

            unique_products = set(t['product_id']
                                  for t in transaction_per_product)
            expected_unique_count = len(unique_products)

            unique_count = calculate_total_unique_field(
                transactions, 'product_id')

            assert unique_count == expected_unique_count


#TODO: Add tests for ProductSummaryView