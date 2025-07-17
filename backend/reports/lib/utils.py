from decimal import Decimal
from django.db.models import QuerySet
from api.models import Transaction
from reports.lib.constants import EXCHANGE_RATES
from lib.logging_config import logger


def calculate_total_amount_PLN(transactions: QuerySet[Transaction] ) -> Decimal:

    total_amount = 0
    for transaction in transactions:
        try:
            rate = EXCHANGE_RATES.get(transaction.currency)
        except KeyError:
            rate = 1
            logger.error(f"Currency {transaction.currency} not found, using default rate of 1.")

        total_amount += transaction.amount* Decimal(rate)
    return total_amount

def calculate_total_unique_field(transactions: QuerySet[Transaction], field: str) -> int:
    unique_fields = set(transactions.values_list(field, flat=True))

    return len(unique_fields)


