from dataclasses import dataclass
from dkapp.models import Contract, AccountingEntry


@dataclass
class PerContractData:
    contract: Contract
    balance: float
    fraction_credit: float
    interest_rate: float
    relative_interest_rate: float


class AverageInterestRateReport:
    def __init__(self, contracts, sum_credit):
        self.sum_credit = sum_credit
        self.per_contract_data = [
            PerContractData(
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
        all_contracts = Contract.objects.all()
        assert AccountingEntry.total_sum() == Contract.total_sum()
        sum_credit = AccountingEntry.total_sum()
        return cls(contracts=all_contracts, sum_credit=sum_credit)
