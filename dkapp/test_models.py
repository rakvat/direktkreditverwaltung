from datetime import date
from decimal import Decimal
from model_bakery import baker
from django.test import TestCase
from dkapp.models import ContractVersion, AccountingEntry



class ContractTestCase(TestCase):
    def setUp(self):
        self.contract = baker.make('dkapp.Contract')
        self.contract_version1 = ContractVersion.objects.create(
            start=date(2019, 2, 10),
            duration_years=10,
            interest_rate=Decimal('0.01'),
            version=1,
            contract=self.contract,
        )
        self.contract_version2 = ContractVersion.objects.create(
            start=date(2020, 1, 10),
            duration_years=10,
            interest_rate=Decimal('0.02'),
            version=2,
            contract=self.contract,
        )
        self.contract_version3 = ContractVersion.objects.create(
            start=date(2020, 3, 31),
            duration_years=10,
            interest_rate=Decimal('0.015'),
            version=3,
            contract=self.contract,
        )
        self.accounting_entries = [
            AccountingEntry.objects.create(
                date=the_date,
                amount=Decimal('100'),
                contract=self.contract,
            ) for the_date in [date(2019, 2, 10), date(2020, 1, 1), date(2020, 1, 15)]
        ]

    def test_last_version(self):
        self.assertEqual(self.contract.last_version, self.contract_version3)

    def test_versions_in(self):
        self.assertEqual(set(self.contract.versions_in(2019)), {self.contract_version1})
        self.assertEqual(set(self.contract.versions_in(2020)), {self.contract_version2, self.contract_version3})

    def test_interest_rate_on(self):
        self.assertEqual(
            self.contract.interest_rate_on(date(2019, 5, 13)),
            Decimal(self.contract_version1.interest_rate),
        )
        self.assertEqual(
            self.contract.interest_rate_on(date(2020, 3, 30)),
            Decimal(self.contract_version2.interest_rate),
        )
        self.assertEqual(
            self.contract.interest_rate_on(date(2020, 3, 31)),
            Decimal(self.contract_version3.interest_rate),
        )

    def test_accounting_entries_in(self):
        self.assertEqual(
            set(self.contract.accounting_entries_in(2019)),
            { self.accounting_entries[0] },
        )
        self.assertEqual(
            set(self.contract.accounting_entries_in(2020)),
            { self.accounting_entries[1], self.accounting_entries[2] },
        )

    def test_balance(self):
        self.assertEqual(self.contract.balance, Decimal('300'))

    def test_balance_on(self):
        self.assertEqual(self.contract.balance_on(date(2019, 1, 1)), Decimal('0'))
        self.assertEqual(self.contract.balance_on(date(2019, 2, 10)), Decimal('100'))
        self.assertEqual(self.contract.balance_on(date(2019, 12, 31)), Decimal('100'))
        self.assertEqual(self.contract.balance_on(date(2020, 1, 1)), Decimal('200'))
        self.assertEqual(self.contract.balance_on(date(2020, 1, 15)), Decimal('300'))

    def test_expiring(self):
        self.assertEqual(self.contract.expiring, date(2030, 3, 31))

    def test_remaining_years(self):
        self.assertGreater(self.contract.remaining_years(),  2030 - date.today().year - 1)
        self.assertGreater(self.contract.remaining_years(date(2021, 12, 31)),  8)
        self.assertLess(self.contract.remaining_years(date(2021, 12, 31)),  9)
