from datetime import date, datetime

from model_bakery import baker
from django.test import TestCase

from decimal import Decimal
from dkapp.models import ContractVersion, AccountingEntry
from dkapp.operations.reports import RemainingContractsReport


class RemainingCategoryReportTestCase(TestCase):
    def setUp(self):
        self.contract_long = baker.make('dkapp.Contract')
        ContractVersion.objects.create(
            start=date(2019, 2, 10),
            duration_years=10,
            interest_rate=Decimal('0.01'),
            version=1,
            contract=self.contract_long,
        )
        AccountingEntry.objects.create(
            date=date(2019, 5, 5),
            amount=Decimal('100'),
            contract=self.contract_long,
        )

        self.contract_medium = baker.make('dkapp.Contract')
        ContractVersion.objects.create(
            start=date(2014, 2, 10),
            duration_years=10,
            interest_rate=Decimal('0.01'),
            version=1,
            contract=self.contract_medium,
        )
        AccountingEntry.objects.create(
            date=date(2014, 5, 5),
            amount=Decimal('200'),
            contract=self.contract_medium,
        )

        self.contract_short = baker.make('dkapp.Contract', number=42)
        ContractVersion.objects.create(
            start=date(2020, 2, 10),
            duration_years=1,
            interest_rate=Decimal('0.01'),
            version=1,
            contract=self.contract_short,
        )
        AccountingEntry.objects.create(
            date=date(2020, 2, 10),
            amount=Decimal('300'),
            contract=self.contract_short,
        )

        self.contract_short2 = baker.make('dkapp.Contract', number=43)
        ContractVersion.objects.create(
            start=date(2020, 8, 10),
            duration_months=6,
            interest_rate=Decimal('0.01'),
            version=1,
            contract=self.contract_short2,
        )
        AccountingEntry.objects.create(
            date=date(2020, 8, 10),
            amount=Decimal('50'),
            contract=self.contract_short2,
        )

    def test_report(self) -> None:
        report = RemainingContractsReport.create(datetime(2020, 12, 31))

        self.assertEqual(report.less_than_one.balance_sum, 350)
        self.assertEqual(report.between_one_and_five.balance_sum, 200)
        self.assertEqual(report.more_than_five.balance_sum, 100)

        self.assertEqual(report.less_than_one.contracts, [
            (self.contract_short, 300),
            (self.contract_short2, 50),
        ])
