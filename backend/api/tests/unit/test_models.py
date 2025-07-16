import pytest

from api.models import Transaction


@pytest.mark.django_db
class TestTransactionModel:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        ...

    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            transaction_id="123e4567-e89b-12d3-a456-426614174000",
            timestamp="2023-10-01T12:00:00Z",
            amount=100.50,
            currency="USD",
            customer_id="123e4567-e89b-12d3-a456-426614174001",
            product_id="123e4567-e89b-12d3-a456-426614174002",
            quantity=2
        )
        assert transaction.transaction_id == "123e4567-e89b-12d3-a456-426614174000"
        assert transaction.amount == 100.50
        assert transaction.currency == "USD"

    