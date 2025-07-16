from django.db import models
import uuid

class Transaction(models.Model):
    transaction_id = models.UUIDField(primary_key=True)
    timestamp = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    customer_id = models.UUIDField()
    product_id = models.UUIDField()
    quantity = models.IntegerField()

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} {self.currency}"


    


