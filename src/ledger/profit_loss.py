from decimal import Decimal

from django.db.models import Sum
from typing import Optional

from common.utils import Numeric
from ledger.models import Account, Ledger


class ProfitLossLine:
    def __init__(self, account: Account, debit: Optional[Numeric], credit: Optional[Numeric]):
        assert account is not None
        assert debit is not None or credit is not None

        self.account = account
        self.debit = Decimal(debit).quantize(Decimal('.01')) if debit is not None else None
        self.credit = Decimal(credit).quantize(Decimal('.01')) if credit is not None else None

    def __eq__(self, other):
        return self.account == other.account and self.debit == other.debit and self.credit == other.credit


class ProfitLoss:
    def __init__(self, ledger: Ledger):
        accounts = Account.objects.filter(type=Account.PROFIT_LOSS)

        self.profit_loss_lines = []
        sum_losses = sum_revenues = 0
        for account in accounts:
            account_losses = ledger.transactions.filter(debit_account=account)
            account_losses_sum = account_losses.aggregate(Sum('amount'))['amount__sum'] or 0
            account_revenues = ledger.transactions.filter(credit_account=account)
            account_revenues_sum = account_revenues.aggregate(Sum('amount'))['amount__sum'] or 0
            account_result = account_revenues_sum - account_losses_sum
            if account_result > 0:
                self.profit_loss_lines.append(ProfitLossLine(account, account_result, None))
            elif account_result < 0:
                self.profit_loss_lines.append(ProfitLossLine(account, None, -account_result))
            sum_losses += account_losses_sum
            sum_revenues += account_revenues_sum

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
