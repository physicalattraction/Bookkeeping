import datetime
from django.db.models import Sum

from common.utils import write_csv
from ledger.models import Account, Transaction


class Balance:
    def __init__(self, date: datetime.date, output_file: str):
        accounts = Account.objects.filter(type=Account.BALANCE)
        debit_transactions = Transaction.objects.filter(debit_account__in=accounts, date__lte=date)
        credit_transactions = Transaction.objects.filter(credit_account__in=accounts, date__lte=date)

        debit_balance_lines = []
        credit_balance_lines = []
        sum_debit = sum_credit = 0
        for account in accounts:
            debit_account_transactions = debit_transactions.filter(debit_account=account)
            sum_account_debit = debit_account_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
            credit_account_transactions = credit_transactions.filter(credit_account=account)
            sum_account_credit = credit_account_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
            if sum_account_credit == sum_account_debit:
                continue
            if account.debit_type == Account.DEBIT:
                debit_balance_lines.append([str(account), '{:.2f}'.format(sum_account_debit - sum_account_credit)])
            else:
                credit_balance_lines.append([str(account), '{:.2f}'.format(sum_account_credit - sum_account_debit)])
            sum_debit += sum_account_debit
            sum_credit += sum_account_credit

        credit_balance_lines.append(['3000 - Equity', '{:.2f}'.format(sum_debit - sum_credit)])

        lines_longer = len(debit_balance_lines) - len(credit_balance_lines)
        if lines_longer > 0:
            credit_balance_lines += [[None, None]] * lines_longer
        elif lines_longer < 0:
            debit_balance_lines += [[None, None]] * -lines_longer

        header = ['Account', 'Debit', 'Account', 'Credit']
        balance_lines = [lines[0] + lines[1] for lines in zip(debit_balance_lines, credit_balance_lines)]
        balance_lines.append(['Total', '{:.2f}'.format(sum_debit), 'Total', '{:.2f}'.format(sum_debit)])
        print(balance_lines)
        write_csv(header, balance_lines, output_file)
