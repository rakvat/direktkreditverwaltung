from datetime import date
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class InterestDataRow:
    date: date
    label: str
    amount: Decimal
    interest_rate: Decimal
    days_left_in_year: int
    fraction_of_year: Decimal
    interest: float


class InterestProcessor:
    def __init__(self, contract, year):
        self.year = year
        self.start_date = date(self.year, 1, 1)
        self.end_date = date(self.year, 12, 31)
        self.contract = contract
        self.calculation_rows = self.calculate_rows()

    @property
    def value(self):
        return sum([row.interest for row in self.calculation_rows])

    def calculate_rows(self):
        interest_rows = [self._saldo_row()]
        accounting_entries = self.contract.accounting_entries_in(self.year)
        for entry in accounting_entries:
            interest_rows.append(self._accounting_row(entry))

        contract_changes = self.contract.versions_in(self.year)
        if not contract_changes:
            return interest_rows

        old_interest_rate = interest_rows[0].interest_rate
        for contract_change in contract_changes:
            if contract_change.id == self.contract.first_version.id:
                continue
            if contract_change.start == self.start_date:
                continue
            if old_interest_rate == contract_change.interest_rate:
                continue

            interest_rows.extend(self._contract_change_rows(contract_change, old_interest_rate))
            old_interest_rate = contract_change.interest_rate

        return interest_rows

    def _saldo_row(self):
        start_balance = self.contract.balance_on(self.start_date)
        interest_rate = self.contract.interest_rate_on(self.start_date)
        interest_for_year = round(start_balance * interest_rate, 2)

        return InterestDataRow(
            date=self.start_date,
            label="Saldo",
            amount=start_balance,
            interest_rate=interest_rate,
            days_left_in_year=360,
            fraction_of_year=1,
            interest=interest_for_year,
        )

    def _accounting_row(self, accounting_entry):
        days_left, fraction_year = self._days_fraction_360(accounting_entry.date)
        interest_rate = self.contract.interest_rate_on(accounting_entry.date)
        interest = round(accounting_entry.amount * fraction_year * interest_rate, 2)
        return InterestDataRow(
            date=accounting_entry.date,
            label="Einzahlung" if accounting_entry.amount > 0 else "Auszahlung",
            amount=accounting_entry.amount,
            interest_rate=interest_rate,
            days_left_in_year=days_left,
            fraction_of_year=fraction_year,
            interest=interest,
        )

    def _contract_change_rows(self, contract_version, old_interest_rate):
        change_balance = self.contract.balance_on(contract_version.start)
        days_left, fraction_year = self._days_fraction_360(contract_version.start)
        interest_before = round(-change_balance * fraction_year * old_interest_rate, 2)
        interest_after = round(change_balance * fraction_year * contract_version.interest_rate, 2)
        return [
            InterestDataRow(
                date=contract_version.start,
                label="Vertragsänderung",
                amount=-change_balance,
                interest_rate=old_interest_rate,
                days_left_in_year=days_left,
                fraction_of_year=fraction_year,
                interest=interest_before,
            ),
            InterestDataRow(
                date=contract_version.start,
                label="Vertragsänderung",
                amount=change_balance,
                interest_rate=contract_version.interest_rate,
                days_left_in_year=days_left,
                fraction_of_year=fraction_year,
                interest=interest_after
            )
        ]

    def _days_fraction_360(self, date):
        days_left = days360_eu(date, self.end_date)
        fraction = Decimal(days_left/360)
        return days_left, fraction


def days360_eu(start_date, end_date):
    start_day = start_date.day
    start_month = start_date.month
    start_year = start_date.year
    end_day = end_date.day
    end_month = end_date.month
    end_year = end_date.year

    if start_day == 31:
        start_day = 30

    if end_day == 31:
        end_day = 30

    return (end_year - start_year) * 360 + (end_month - start_month) * 30 + (end_day - start_day)
