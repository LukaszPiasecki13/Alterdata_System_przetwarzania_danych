from django.db import models

class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    customer_id = models.IntegerField()
    product_id = models.IntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} {self.currency}"


    


