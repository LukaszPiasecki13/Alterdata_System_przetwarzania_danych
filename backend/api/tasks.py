from celery import shared_task
import csv
import io
from rest_framework.exceptions import ValidationError


from .serializers import TransactionSerializer
from lib.logging_config import logger


@shared_task
def process_csv_file(file_data):

    try:
        decoded_file = file_data.decode('utf-8')
    except UnicodeDecodeError as e:
        logger.error(f"Error decoding file: {e}")
        raise ValidationError({"error": "Invalid file format. Please upload a valid CSV file."}, status=400)

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

    return {'errors': errors}