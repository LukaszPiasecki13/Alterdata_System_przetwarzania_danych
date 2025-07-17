import io
import csv
import pytest
import uuid
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from api.models import Transaction
from lib.TransactionFactory import TransactionFactory
from api.paginators import TransactionPaginator


LOOP_COUNT = 25

@pytest.mark.django_db
class TestTransactionViews:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.factory = TransactionFactory()
        user = User.objects.create_user(username="testuser", password="testpass123")

        self.client.force_authenticate(user=user)


    def generate_csv_file(self, transactions_data):
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=transactions_data[0].keys())
        writer.writeheader()
        for row in transactions_data:
            writer.writerow(row)
        output.seek(0)
        return io.BytesIO(output.read().encode("utf-8"))

    def test_upload_valid_csv(self):
        transactions_data = []
        for _ in range(LOOP_COUNT):  
            transactions_data.append(
                self.factory.generate_transaction_data(allow_duplicates=True))
            
        csv_file = self.generate_csv_file(transactions_data)
        csv_file.name = "file.csv"

        response = self.client.post(
            reverse("transactions-upload"),
            data={"file": csv_file}
        )

        assert response.status_code == 200
        assert Transaction.objects.count() == LOOP_COUNT

    def test_list_transactions_with_filtering(self):
        t1 = Transaction.objects.create(**self.factory.generate_transaction_data(allow_duplicates=True))

        for _ in range(LOOP_COUNT-1):
            Transaction.objects.create(**self.factory.generate_transaction_data(allow_duplicates=True))

        response = self.client.get(
            reverse("transactions-list"),
            data={"customer_id": t1.customer_id}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["results"]
        customer_ids = {item["customer_id"] for item in data["results"]}
        assert customer_ids == {str(t1.customer_id)}

    def test_list_transactions_without_filtering_pagination(self):
        backup_data = []
        for _ in range(LOOP_COUNT):
            transaction_data = self.factory.generate_transaction_data(
                allow_duplicates=True)
            _ = Transaction.objects.create(**transaction_data)
            backup_data.append(transaction_data)

        response = self.client.get(reverse("transactions-list"))
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert data["count"] == LOOP_COUNT
        assert len(data["results"]) == TransactionPaginator.page_size  

    def test_transaction_detail_view(self):
        transaction = Transaction.objects.create(**self.factory.generate_transaction_data(allow_duplicates=True))

        response = self.client.get(
            reverse("transactions-detail", kwargs={'transaction_id': transaction.transaction_id})
        )
        
        assert response.status_code == 200
        assert response.data["transaction_id"] == str(transaction.transaction_id)
        assert response.data["customer_id"] == str(transaction.customer_id)
        assert response.data["product_id"] == str(transaction.product_id)
        assert response.data["amount"] == str(transaction.amount)
        assert response.data["currency"] == transaction.currency
        assert response.data["quantity"] == int(transaction.quantity)
        

    def test_transaction_detail_not_found(self):

        fake_id = uuid.uuid4()
        response = self.client.get(
            reverse("transactions-detail", args=[fake_id])
        )
        assert response.status_code == 404