from decimal import Decimal

from django.db.models import Sum
from typing import Optional, Union

from common.utils import write_csv
from ledger.models import Account, Transaction, Ledger

Numeric = Union[Decimal, float, int]
SEPARATOR = ','
LINETERMINATOR = '\n'


class ProfitLossLine:
    def __init__(self, account: Account, debit: Optional[Numeric], credit: Optional[Numeric]):
        self.account = account
        self.debit = Decimal(debit).quantize(Decimal('.01')) if debit is not None else None
        self.credit = Decimal(credit).quantize(Decimal('.01')) if credit is not None else None

    def __repr__(self):
        return SEPARATOR.join([str(element) if element is not None else ''
                               for element in [self.account.name, self.debit, self.credit]])

    def __eq__(self, other):
        return self.account == other.account and self.debit == other.debit and self.credit == other.credit


class ProfitLoss:
    HEADER = SEPARATOR.join(['Description', 'Debit', 'Credit'])

    def __init__(self, year: int):
        # TODO: Input for who to make the PL, instead of assuming there is only one ledger per year
        ledger = Ledger.objects.get(year=year)
        accounts = Account.objects.filter(type=Account.PROFIT_LOSS)

        self.profit_loss_lines = []
        sum_losses = sum_revenues = 0
        for account in accounts:
            account_losses = ledger.transactions.filter(debit_account=account).aggregate(Sum('amount'))['amount__sum'] or 0
            account_revenues = ledger.transactions.filter(credit_account=account).aggregate(Sum('amount'))['amount__sum'] or 0
            account_result = account_revenues - account_losses
            if account_result > 0:
                self.profit_loss_lines.append(ProfitLossLine(account.name, account_result, None))
            elif account_result < 0:
                self.profit_loss_lines.append(ProfitLossLine(account.name, None, -account_result))
            sum_losses += account_losses
            sum_revenues += account_revenues

        result = sum_revenues - sum_losses
        if result > 0:
            profit, _ = Account.objects.get_or_create(chart=ledger.chart, name='Profit',
                                                   defaults={'code': 5999, 'type': Account.PROFIT_LOSS,
                                                             'debit_type': Account.DEBIT})

            self.total = ProfitLossLine(profit, result, None)
        elif result < 0:
            loss, _ = Account.objects.get_or_create(chart=ledger.chart, name='Loss',
                                                 defaults={'code': 4999, 'type': Account.PROFIT_LOSS,
                                                           'debit_type': Account.CREDIT})
            self.total = ProfitLossLine(loss, None, -result)


    def __repr__(self):
        return LINETERMINATOR.join([self.HEADER] + [repr(pll) for pll in self.profit_loss_lines + [self.total]])

    def save(self, output_file: str):
        write_csv(self.HEADER, self.profit_loss_lines, output_file)
