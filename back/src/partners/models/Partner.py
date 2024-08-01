from django.db import models
from common import BaseModel


class Partner(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    tax_id = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    credit_term = models.IntegerField(help_text="Tiempo de crédito en días")
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    bank_address = models.CharField(max_length=255)
    swift_code = models.CharField(max_length=50)
    iban = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    contact_name = models.CharField(max_length=100)
    export_code = models.CharField(max_length=50)

    def __str__(self):
        return self.name
