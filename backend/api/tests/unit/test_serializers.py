import pytest
import uuid

from api.serializers import TransactionSerializer, CsvFileSerializer
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.fixture
def create_file():
    def _create_file(name, content, content_type):
        return SimpleUploadedFile(name, content.encode(), content_type=content_type)
    return _create_file

@pytest.mark.django_db
class TestCsvFileSerializer:

    @pytest.fixture(autouse=True)
    def setup_method(self, create_file):
        self.content = "transaction_id,timestamp,amount,currency,customer_id,product_id,quantity\n"
        "d4a3f861-6c22-44f7-8121-09df0d5b79f3,2025-07-14T12:15:30Z,199.99,PLN,f3a2e210-bd6a-49c9-812e-bd4b23cd1e12,aa12e3f5-987a-48ec-802a-d0c821fef302,2"


    def test_csv_file_serializer_valid(self, create_file):
        file = create_file("test.csv", self.content, "text/csv")
        serializer = CsvFileSerializer(data={'file': file})
        assert serializer.is_valid()
        assert serializer.validated_data['file'] == file

    def test_csv_file_serializer_invalid_file_type(self, create_file):
        file = create_file("test.txt", self.content, "text/plain")
        serializer = CsvFileSerializer(data={'file': file})
        assert not serializer.is_valid()
        assert 'file' in serializer.errors
        assert 'File must be a CSV.' in serializer.errors['file']

    def test_csv_file_serializer_invalid_extension(self, create_file):
        file = create_file("test.txt", self.content, "text/csv")
        serializer = CsvFileSerializer(data={'file': file})
        assert not serializer.is_valid()
        assert 'file' in serializer.errors
        assert 'File must be a CSV.' in serializer.errors['file']

    def test_csv_file_serializer_too_large(self, create_file):
        file = create_file("test.csv", self.content * int(50 * 1024 * 1024/73 +1), "text/csv")  # 51MB
        serializer = CsvFileSerializer(data={'file': file})
        assert not serializer.is_valid()
        assert 'file' in serializer.errors
        assert any("File size must not exceed 5 MB," in str(err) for err in serializer.errors['file'])

    def test_csv_file_serializer_empty(self, create_file):
        file = create_file("empty.csv", "", "text/csv")
        serializer = CsvFileSerializer(data={'file': file})
        assert not serializer.is_valid()
        assert 'file' in serializer.errors
        assert 'The submitted file is empty.' in serializer.errors['file']


@pytest.mark.django_db
class TestTransactionSerializer:

    @pytest.fixture
    def valid_data(self):
        return {
            "transaction_id": str(uuid.uuid4()),
            "timestamp": "2025-07-14T12:15:30Z",
            "amount": '199.99',
            "currency": "pln",
            "customer_id": str(uuid.uuid4()),
            "product_id": str(uuid.uuid4()),
            "quantity": '3'
        }
   

    def test_valid_transaction(self, valid_data):
        serializer = TransactionSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['currency'] == "PLN"
        

    def test_invalid_transaction_id(self, valid_data):
        valid_data['transaction_id'] = 'invalid-uuid'
        serializer = TransactionSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'transaction_id' in serializer.errors
        assert "Must be a valid UUID." in serializer.errors['transaction_id']

    def test_invalid_customer_id(self, valid_data):
        valid_data['customer_id'] = 'asdassdsad'
        serializer = TransactionSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'customer_id' in serializer.errors
        assert "Must be a valid UUID." in serializer.errors['customer_id']

    def test_invalid_product_id(self, valid_data):
        valid_data['product_id'] = '123'
        serializer = TransactionSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'product_id' in serializer.errors
        assert "Must be a valid UUID." in serializer.errors['product_id']

    def test_invalid_timestamp_format(self, valid_data):
        valid_data['timestamp'] = '2025/07/14 12:15:30'
        serializer = TransactionSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'timestamp' in serializer.errors
        assert any("Datetime has wrong format" in str(err) for err in serializer.errors['timestamp'])   # Django validation error

    def test_missing_timestamp(self, valid_data):
        valid_data['timestamp'] = None
        serializer = TransactionSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'timestamp' in serializer.errors
        assert "This field may not be null." in serializer.errors['timestamp']  # Django validation error

    def test_negative_amount(self, valid_data):
        valid_data['amount'] = -100
        serializer = TransactionSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'amount' in serializer.errors
        assert "Amount must be greater than zero." in serializer.errors['amount']

    def test_invalid_amount_format(self, valid_data):
        valid_data['amount'] = "abc"
        serializer = TransactionSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'amount' in serializer.errors
        assert "A valid number is required." in serializer.errors['amount'] # Django validation error

    def test_invalid_currency_length(self, valid_data):
        valid_data['currency'] = "PL"
        serializer = TransactionSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'currency' in serializer.errors
        assert "Currency must be a 3-letter code." in serializer.errors['currency']

    def test_negative_quantity(self, valid_data):
        valid_data['quantity'] = -5
        serializer = TransactionSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'quantity' in serializer.errors
        assert "Quantity cannot be negative." in serializer.errors['quantity']

    def test_invalid_quantity_format(self, valid_data):
        valid_data['quantity'] = "ten"
        serializer = TransactionSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'quantity' in serializer.errors
        assert "A valid integer is required." in serializer.errors['quantity']  # Django validation error
