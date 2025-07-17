import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from uuid import uuid4
from datetime import datetime, timedelta

from api.models import Transaction
from reports.lib.constants import EXCHANGE_RATES
from lib.TransactionFactory import TransactionFactory

LOOP_COUNT = 25


@pytest.mark.django_db
class TestCustomerSummaryView:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        factory = TransactionFactory()
        self.client = APIClient()
        user = User.objects.create_user(username="testuser", password="testpass123")

        self.client.force_authenticate(user=user)
        self.backup_data = []

        for _ in range(LOOP_COUNT):
            transaction_data = factory.generate_transaction_data(
                allow_duplicates=True)
            _ = Transaction.objects.create(**transaction_data)
            self.backup_data.append(transaction_data)

    def test_customer_summary_view(self):
        for customer_id in set([tr['customer_id'] for tr in self.backup_data]):
            transactions_per_customer = [
                trs for trs in self.backup_data if trs['customer_id'] == customer_id]
            url = f"/reports/customer-summary/{customer_id}/"
            response = self.client.get(url)
            assert response.status_code == 200

            data = response.json()

            expected_total_amount_PLN = sum(
                Decimal(tr['amount']) * Decimal(EXCHANGE_RATES[tr['currency']])
                for tr in transactions_per_customer
            )

            unique_products = set([tr['product_id']
                                  for tr in transactions_per_customer])
            earliest_timestamp = min(tr['timestamp']
                                     for tr in transactions_per_customer)

            assert data["customer_id"] == customer_id
            assert round(Decimal(data["total_amount_PLN"]), 2) == round(
                expected_total_amount_PLN, 2)
            assert data["total_unique_products"] == len(unique_products)
            assert earliest_timestamp in data["earliest_transaction_date"].replace("Z", "+00:00")

    def test_customer_summary_not_found(self):
        url = f"/reports/customer-summary/{uuid4()}/"
        response = self.client.get(url)
        assert response.status_code == 404
        assert "error" in response.json()

    def test_customer_summary_with_date_filter(self):

        customer_id = self.backup_data[0]['customer_id']
        transactions_per_customer = [tr for tr in self.backup_data if tr['customer_id'] == customer_id]


        timestamps = sorted([datetime.fromisoformat(tr['timestamp']) for tr in transactions_per_customer])
        start_date = timestamps[0].strftime('%Y-%m-%d') 
        end_date = timestamps[-1].strftime('%Y-%m-%d')

        url = f"/reports/customer-summary/{customer_id}/"
        response = self.client.get(url, data={"start_date": start_date, "end_date": end_date})
        assert response.status_code == 200

        data = response.json()


        filtered_transactions = [
            tr for tr in transactions_per_customer
            if start_date <= tr['timestamp'] <= end_date
        ]

        expected_total_amount_PLN = sum(
            Decimal(tr['amount']) * Decimal(EXCHANGE_RATES[tr['currency']])
            for tr in filtered_transactions
        )
        unique_products = set(tr['product_id'] for tr in filtered_transactions)
        earliest_timestamp = min(tr['timestamp'] for tr in filtered_transactions)

        assert abs(Decimal(data["total_amount_PLN"])-expected_total_amount_PLN) < Decimal('0.01')

        assert data["total_unique_products"] == len(unique_products)
        assert earliest_timestamp in data["earliest_transaction_date"].replace("Z", "+00:00")


@pytest.mark.django_db
class TestProductSummaryView:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        factory = TransactionFactory()
        self.client = APIClient()
        user = User.objects.create_user(username="testuser", password="testpass123")

        self.client.force_authenticate(user=user)
        self.backup_data = []

        for _ in range(LOOP_COUNT):
            transaction_data = factory.generate_transaction_data(
                allow_duplicates=True)
            _ = Transaction.objects.create(**transaction_data)
            self.backup_data.append(transaction_data)

    def test_product_summary_view(self):
        for product_id in set([tr['product_id'] for tr in self.backup_data]):
            transactions_per_product = [
                trs for trs in self.backup_data if trs['product_id'] == product_id]

            url = f"/reports/product-summary/{product_id}/"
            response = self.client.get(url)
            assert response.status_code == 200

            data = response.json()

            total_quantity = sum(int(tr['quantity'])
                                 for tr in transactions_per_product)
            expected_amount = sum(
                Decimal(tr['amount']) * Decimal(EXCHANGE_RATES[tr['currency']])
                for tr in transactions_per_product
            )
            unique_customers = set([tr['customer_id']
                                   for tr in transactions_per_product])

            assert data["product_id"] == product_id
            assert data["total_quantity"] == total_quantity
            assert abs(Decimal(data["total_amount_PLN"]) -
                       expected_amount) < Decimal('0.01')
            assert data["total_unique_customers"] == len(unique_customers)

    def test_product_summary_not_found(self):
        url = f"/reports/product-summary/{uuid4()}/"
        response = self.client.get(url)
        assert response.status_code == 404
        assert "error" in response.json()


    def test_product_summary_view_with_date_filter(self):
        for product_id in set(tr['product_id'] for tr in self.backup_data):
            transactions_per_product = [
                tr for tr in self.backup_data if tr['product_id'] == product_id
            ]


            timestamps = sorted([datetime.fromisoformat(tr['timestamp']) for tr in transactions_per_product])
            start_date = timestamps[0].strftime('%Y-%m-%d')
            end_date = timestamps[-1].strftime('%Y-%m-%d')

            url = f"/reports/product-summary/{product_id}/"
            response = self.client.get(url, data={"start_date": start_date, "end_date": end_date})
            assert response.status_code == 200

            data = response.json()

            filtered_transactions = [
                tr for tr in transactions_per_product
                if start_date <= tr['timestamp'][:10] <= end_date
            ]

            total_quantity = sum(int(tr['quantity']) for tr in filtered_transactions)
            expected_amount = sum(
                Decimal(tr['amount']) * Decimal(EXCHANGE_RATES[tr['currency']])
                for tr in filtered_transactions
            )
            unique_customers = set(tr['customer_id'] for tr in filtered_transactions)

            assert data["product_id"] == product_id
            assert data["total_quantity"] == total_quantity
            assert abs(Decimal(data["total_amount_PLN"]) -
                       expected_amount) < Decimal('0.01')
            assert data["total_unique_customers"] == len(unique_customers)
