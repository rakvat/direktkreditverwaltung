from datetime import date
from decimal import Decimal
from model_bakery import baker
from django.test import TestCase
from dkapp.models import ContractVersion, AccountingEntry
from dkapp.operations.interest import InterestProcessor, days360_eu


class Days360euTestCase(TestCase):
    def test_31th(self):
        self.assertEqual(days360_eu(date(2020, 2, 28), date(2020,3, 28)), 30)
        self.assertEqual(days360_eu(date(2020, 2, 29), date(2020,3, 29)), 30)
        self.assertEqual(days360_eu(date(2020, 2, 28), date(2020,3, 30)), 32)
        self.assertEqual(days360_eu(date(2020, 2, 28), date(2020,3, 31)), 32)
        self.assertEqual(days360_eu(date(2020, 2, 28), date(2020,4, 1)), 33)
        self.assertEqual(days360_eu(date(2019, 2, 28), date(2020,3, 31)), 392)


class InterestProcessorTestCase(TestCase):
    def setUp(self):
        self.contract = baker.make('dkapp.Contract')

    def test_full_year(self):
        ContractVersion.objects.create(
            start=date(2019, 2, 10),
            duration_years=10,
            interest_rate=Decimal('0.01'),
            version=1,
            contract=self.contract,
        )
        AccountingEntry.objects.create(
            date=date(2019, 5, 5),
            amount=Decimal('100'),
            contract=self.contract,
        )

        self.processor = InterestProcessor(self.contract, 2020)

        self.assertEqual(len(self.processor.calculation_rows), 1)
        self.assertEqual(self.processor.calculation_rows[0].amount, Decimal('100'))
        self.assertEqual(self.processor.value, Decimal('1.0'))

    def test_part_year(self):
        ContractVersion.objects.create(
            start=date(2019, 2, 10),
            duration_years=10,
            interest_rate=Decimal('0.01'),
            version=1,
            contract=self.contract,
        )
        AccountingEntry.objects.create(
                date=date(2020, 7, 1),
            amount=Decimal('100'),
            contract=self.contract,
        )

        self.processor = InterestProcessor(self.contract, 2020)

        self.assertEqual(len(self.processor.calculation_rows), 2)
        self.assertEqual(self.processor.calculation_rows[0].amount, Decimal('0'))
        self.assertEqual(self.processor.calculation_rows[1].amount, Decimal('100'))
        self.assertEqual(self.processor.value, Decimal('0.5'))

    def test_part_year_with_contract_change(self):
        ContractVersion.objects.create(
            start=date(2019, 2, 10),
            duration_years=10,
            interest_rate=Decimal('0.01'),
            version=1,
            contract=self.contract,
        )
        AccountingEntry.objects.create(
                date=date(2019, 10, 1),
            amount=Decimal('100'),
            contract=self.contract,
        )

        self.processor = InterestProcessor(self.contract, 2019)

        self.assertEqual(len(self.processor.calculation_rows), 4)
        self.assertEqual(self.processor.calculation_rows[0].amount, Decimal('0'))
        self.assertEqual(self.processor.calculation_rows[1].amount, Decimal('100'))
        self.assertEqual(self.processor.calculation_rows[2].amount, Decimal('0'))
        self.assertEqual(self.processor.calculation_rows[3].amount, Decimal('0'))
        self.assertEqual(self.processor.value, Decimal('0.25'))

    def test_added_amount_in_year(self):
        ContractVersion.objects.create(
            start=date(2019, 2, 10),
            duration_years=10,
            interest_rate=Decimal('0.01'),
            version=1,
            contract=self.contract,
        )
        AccountingEntry.objects.create(
            date=date(2019, 5, 5),
            amount=Decimal('100'),
            contract=self.contract,
        )
        AccountingEntry.objects.create(
            date=date(2020, 4, 1),
            amount=Decimal('100'),
            contract=self.contract,
        )

        self.processor = InterestProcessor(self.contract, 2020)

        self.assertEqual(len(self.processor.calculation_rows), 2)
        self.assertEqual(self.processor.calculation_rows[0].amount, Decimal('100'))
        self.assertEqual(self.processor.calculation_rows[1].amount, Decimal('100'))
        self.assertEqual(self.processor.value, Decimal('1.75'))

    def test_contract_change_in_year(self):
        ContractVersion.objects.create(
            start=date(2019, 2, 10),
            duration_years=10,
            interest_rate=Decimal('0.01'),
            version=1,
            contract=self.contract,
        )
        AccountingEntry.objects.create(
            date=date(2019, 5, 5),
            amount=Decimal('100'),
            contract=self.contract,
        )
        ContractVersion.objects.create(
            start=date(2020, 7, 1),
            duration_years=10,
            interest_rate=Decimal('0.005'),
            version=2,
            contract=self.contract,
        )

        self.processor = InterestProcessor(self.contract, 2020)

        self.assertEqual(len(self.processor.calculation_rows), 3)
        self.assertEqual(self.processor.calculation_rows[0].amount, Decimal('100'))
        self.assertEqual(self.processor.calculation_rows[1].amount, Decimal('-100'))
        self.assertEqual(self.processor.calculation_rows[2].amount, Decimal('100'))
        self.assertEqual(self.processor.value, Decimal('0.75'))
