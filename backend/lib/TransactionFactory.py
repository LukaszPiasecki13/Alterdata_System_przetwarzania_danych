
import uuid
import random
from decimal import Decimal
from datetime import datetime, timedelta, timezone




class TransactionFactory:
    CURRENCIES = ["PLN", "EUR", "USD"]
    CUST_ID = [
    uuid.UUID("d9d179a4-df12-4dbe-9a2b-41a7cd33d8fb"),
    uuid.UUID("aa3e8e0e-8a1f-4639-a297-3c61dc5e021b"),
    uuid.UUID("2b6d92c0-5696-4b7a-9a9b-5d96b0f4a9d5"),
    uuid.UUID("18a3ff68-8fc2-4894-84f0-2c8c64e82cf5"),
    uuid.UUID("cfc2d299-0e4b-44e0-83c9-2b9292793c2d"),
    uuid.UUID("10afc40d-e71c-4d3e-8fc0-fd027fcd47b2"),
    uuid.UUID("3ff4d250-12a4-4b43-8f38-8b7db2079f4f"),
    uuid.UUID("3b47c770-8f1e-4f02-a5cc-d47328784db9"),
    uuid.UUID("985a50ac-55b1-4a87-bd06-d4743c83b23a"),
    uuid.UUID("a2d6c818-bb11-4432-8cd7-bc42124ff1de"),
    ]
    PROD_ID = [
    uuid.UUID("17275d67-8054-46de-b621-8e7c6db342c5"),
    uuid.UUID("ba372087-bd00-4fc0-8028-8ae4b37b35d6"),
    uuid.UUID("540728f5-2870-4536-bc2a-53a3f3b65761"),
    uuid.UUID("82b8bbd3-b2de-4c89-a19e-e1aa13f02e7e"),
    uuid.UUID("49dded74-775e-4b4a-8b46-671426e18095"),
    uuid.UUID("ec8466d7-3892-4de5-bc5d-e6c2b0a6b2ef"),
    uuid.UUID("3c180122-c963-46d7-9d18-58e71d52491d"),
    uuid.UUID("5e2292f6-1f75-4a36-b660-c06318ea166f"),
    uuid.UUID("dcb86e52-03d3-4ec1-a350-e7294f6bcd6a"),
    uuid.UUID("6a011d79-4e50-414e-92c2-0cfd68e4c1b6"),
    ]


    def __init__(self):
        self.cust_id_list = self.CUST_ID.copy() 
        self.prod_id_list = self.PROD_ID.copy()


    def _random_amount(self):
        return Decimal(f"{random.uniform(1.0, 100.0):.2f}")

    def _random_quantity(self):
        return random.randint(1, 10)

    def _random_currency(self):
        return random.choice(self.CURRENCIES)

    def _random_timestamp(self):
        now = datetime.now(timezone.utc)
        days_offset = random.randint(-365, 0)
        return now + timedelta(days=days_offset)
    
    def _generate_id(self, id_list=None, allow_duplicates=False):

        if len(id_list) == 0:
            return None

        if allow_duplicates == False:
            id = random.choice(id_list)
            id_list.remove(id)
        else:
            id = random.choice(id_list)

        return id


    def generate_transaction_data(self, allow_duplicates: bool = False) -> dict:

        return {
            "transaction_id": str(uuid.uuid4()),
            "timestamp": str(self._random_timestamp().isoformat()),
            "amount": str(self._random_amount()),
            "currency": self._random_currency(),
            "customer_id": str(self._generate_id(self.cust_id_list, allow_duplicates)),
            "product_id": str(self._generate_id(self.prod_id_list, allow_duplicates)),
            "quantity": str(self._random_quantity()),
        }