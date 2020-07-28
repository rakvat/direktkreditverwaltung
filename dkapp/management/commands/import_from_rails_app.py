import sqlite3
import pytz

from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
from django.core.management.base import BaseCommand, CommandError
from dkapp.models import Contact, Contract, ContractVersion, AccountingEntry


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Command(BaseCommand):
    help = 'Import sqlite3 file'

    def import_contacts(self):
        for row in self.c.execute('SELECT * FROM contacts'):
            contact = Contact(
                id=row['id'],
                first_name=row['prename'],
                last_name=row['name'],
                address=row['address'],
                iban=row['account_number'],
                bic=row['bank_number'],
                created_at=pytz.timezone(settings.TIME_ZONE).localize(parse_datetime(row['created_at'])),
                updated_at=pytz.timezone(settings.TIME_ZONE).localize(parse_datetime(row['updated_at'])),
                email=row['email'],
                phone=row['phone'],
                remark=row['remark'],
                bank_name=row['bank_name'],
            )
            contact.save()

    def import_contracts(self):
        for row in self.c.execute('SELECT * FROM contracts'):
            contact = Contract(
                id=row['id'],
                number=row['number'],
                comment=row['comment'],
                category=row['category'],
                contact=Contact.objects.get(pk=row['contact_id']),
                created_at=pytz.timezone(settings.TIME_ZONE).localize(parse_datetime(row['created_at'])),
                updated_at=pytz.timezone(settings.TIME_ZONE).localize(parse_datetime(row['updated_at'])),
            )
            contact.save()


    def import_contract_versions(self):
        for row in self.c.execute('SELECT * FROM contract_versions'):
            contact = ContractVersion(
                id=row['id'],
                start=parse_date(row['start']),
                duration_months=row['duration_months'],
                duration_years=row['duration_years'],
                interest_rate=row['interest_rate'],
                version=row['version'],
                contract=Contract.objects.get(pk=row['contract_id']),
                created_at=pytz.timezone(settings.TIME_ZONE).localize(parse_datetime(row['created_at'])),
                updated_at=pytz.timezone(settings.TIME_ZONE).localize(parse_datetime(row['updated_at'])),
            )
            contact.save()

    def import_accounting_entries(self):
        for row in self.c.execute('SELECT * FROM accounting_entries'):
            contact = AccountingEntry(
                id=row['id'],
                date=parse_date(row['date']),
                amount=row['amount'],
                contract=Contract.objects.get(pk=row['contract_id']),
                created_at=pytz.timezone(settings.TIME_ZONE).localize(parse_datetime(row['created_at'])),
                updated_at=pytz.timezone(settings.TIME_ZONE).localize(parse_datetime(row['updated_at'])),
            )
            contact.save()

    def import_from_sqlite(self, sqlite3_path):
        db = sqlite3.connect(sqlite3_path)
        db.row_factory = dict_factory
        self.c = db.cursor()

        self.import_contacts()
        self.import_contracts()
        self.import_contract_versions()
        self.import_accounting_entries()
        db.close()

    def clear_all(self):
        Contact.objects.all().delete()

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='path to the sqlite3 file to import')

    def handle(self, *args, **options):
        self.clear_all()
        self.import_from_sqlite(sqlite3_path=options['path'])
        self.stdout.write(self.style.SUCCESS('Successfully imported'))
