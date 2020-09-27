from typing import List
from dataclasses import dataclass
from dkapp.models import Contact, Contract, AccountingEntry
from dkapp.operations.interest import InterestProcessor, InterestDataRow


@dataclass
class FractionPerContract:
    contract: Contract
    balance: float
    fraction_credit: float
    interest_rate: float
    relative_interest_rate: float


class AverageInterestRateReport:
    def __init__(self, contracts, sum_credit):
        self.sum_credit = sum_credit
        self.per_contract_data = [
            FractionPerContract(
                contract=contract,
                balance=balance,
                fraction_credit=(fraction:=balance/sum_credit),
                interest_rate=(interest_rate:=contract.last_version.interest_rate),
                relative_interest_rate=interest_rate * fraction,
                ) for contract in contracts if (balance:=contract.balance) > 0
        ]
        self.avg_interest_rate = sum([data.relative_interest_rate for data in self.per_contract_data])

    @classmethod
    def create(cls):
        all_contracts = Contract.objects.order_by('number')
        assert AccountingEntry.total_sum() == Contract.total_sum()
        sum_credit = AccountingEntry.total_sum()
        return cls(contracts=all_contracts, sum_credit=sum_credit)


@dataclass
class InterestPerContract:
    contract: Contract
    contact: Contact
    interest: float
    interest_rows: List[InterestDataRow]


class InterestTransferListReport:
    def __init__(self, year, contracts):
        self.per_contract_data = [
            InterestPerContract(
                contract=contract,
                contact=contract.contact,
                interest=interest_processor.value,
                interest_rows=interest_processor.calculation_rows,
            ) for contract in contracts
            if (interest_processor:=InterestProcessor(contract, year)).value > 0
        ]
        self.sum_interest = sum([data.interest for data in self.per_contract_data])

    @classmethod
    def create(cls, year):
        all_contracts = Contract.objects.order_by('number').prefetch_related('contact')
        return cls(year, contracts=all_contracts)
