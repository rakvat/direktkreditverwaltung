from django.db import models


class Contact(models.Model):
    last_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    iban = models.CharField(max_length=200, blank=True)
    bic = models.CharField(max_length=200, blank=True)
    bank_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=200, blank=True)
    email = models.CharField(max_length=200, blank=True)
    remark = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField() # add back after import auto_now_add=True)
    updated_at = models.DateTimeField() # add back after import auto_now=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class Contract(models.Model):
    class Category(models.TextChoices):
        PRIVAT = 'Privat'
        SYNDIKAT = 'Syndikat'
        DRITTE = 'Dritte'

    number = models.IntegerField()
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=200, choices=Category.choices)
    created_at = models.DateTimeField() # add back after import auto_now_add=True)
    updated_at = models.DateTimeField() # add back after import auto_now=True)


class ContractVersion(models.Model):
    start = models.DateField()
    duration_months = models.IntegerField(null=True, blank=True)
    duration_years = models.IntegerField(null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=4)
    version = models.IntegerField()
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    created_at = models.DateTimeField() # add back after import auto_now_add=True)
    updated_at = models.DateTimeField() # add back after import auto_now=True)


class AccountingEntry(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    created_at = models.DateTimeField() # add back after import auto_now_add=True)
    updated_at = models.DateTimeField() # add back after import auto_now=True)
