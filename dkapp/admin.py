from django.contrib import admin

from .models import Contact, Contract, ContractVersion, AccountingEntry

admin.site.register(Contact)
admin.site.register(Contract)
admin.site.register(ContractVersion)
admin.site.register(AccountingEntry)
