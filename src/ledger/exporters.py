import os.path

from django.utils import timezone

from common.utils import Matrix, concatenate_matrices, sum_available_elements, write_xlsx
from ledger.balance import Balance
from ledger.models import Ledger
from ledger.profit_loss import ProfitLoss


class LedgerExporter:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.profit_loss = ProfitLoss(ledger=self.ledger)
        end_of_year = timezone.datetime(year=self.ledger.year, month=12, day=31).date()
        self.balance = Balance(end_of_year)

    def write_ledger_to_xlsx(self, full_path_to_file: str) -> None:
        # TODO: Remove contact from transaction, it's already on the associated account
        # TODO: Support transactions with multiple credit and debit accounts
        # TODO: Set the value columns to currency €
        contents = self._generate_contents_from_ledger(self.ledger)
        write_xlsx(contents, full_path_to_file)

    def write_profit_loss_to_xlsx(self, full_path_to_file: str) -> None:
        """
        Write the given profit loss to an Excel file

        :param full_path_to_file: Full path to a file
        """

        contents = self._generate_contents_from_profit_loss(self.profit_loss)
        write_xlsx(contents, full_path_to_file)

    def write_balance_to_xlsx(self, full_path_to_file: str) -> None:
        """
        Write the given balance to an Excel file

        :param full_path_to_file: Full path to a file
        """

        contents = self._generate_contents_from_balance(self.balance)
        write_xlsx(contents, full_path_to_file)

    def write_full_financials_to_xlsx(self, full_path_to_file: str) -> None:
        """
        Write the given profit loss and balance to an Excel file, each in a separate worksheet

        :param full_path_to_file: Full path to a file
        """

        profit_loss_contents = self._generate_contents_from_profit_loss(self.profit_loss)
        if os.path.splitext(full_path_to_file)[-1] == '':
            full_path_to_file += '.xlsx'
        workbook = write_xlsx(profit_loss_contents, full_path_to_file, worksheet_name='PL')

        balance_contents = self._generate_contents_from_balance(self.balance)
        write_xlsx(balance_contents, full_path_to_file, workbook=workbook, worksheet_name='Balance')

    def _generate_contents_from_ledger(self, ledger: Ledger) -> Matrix:
        transactions = ledger.transactions.all()
        header = ['ID', 'Date', 'Description', 'Invoice number', 'Contact',
                  'Account code', 'Account name', 'Debit', 'Credit']
        contents = [header]
        for index, transaction in enumerate(transactions, start=1):
            debit_contact = transaction.debit_account.contact.name if transaction.debit_account.contact else None
            credit_contact = transaction.credit_account.contact.name if transaction.credit_account.contact else None
            contents.append(
                [index, transaction.date, transaction.description, transaction.invoice_number, debit_contact,
                 transaction.debit_account.code, transaction.debit_account.name, transaction.amount, None])
            contents.append([None, None, None, None, credit_contact,
                             transaction.credit_account.code, transaction.credit_account.name, None,
                             transaction.amount])
        return contents

    def _generate_contents_from_profit_loss(self, profit_loss) -> Matrix:
        """
        Generate the contents from a Profit Loss

        :param profit_loss: ProfitLoss to export
        :return: Matrix-shaped contents
        """

        header = ['Account', 'Description', 'Debit', 'Credit']
        contents = [header]
        for line in profit_loss.profit_loss_lines:
            contents.append([line.account.code, line.account.name, line.debit, line.credit])

        total_debit = sum_available_elements(line.debit for line in profit_loss.profit_loss_lines)
        total_credit = sum_available_elements(line.credit for line in profit_loss.profit_loss_lines)
        # TODO: Create a transaction that goes on the balance
        if total_debit > total_credit:
            profit = total_debit - total_credit
            contents.append([None, 'Winst', None, profit])
        elif total_debit < total_credit:
            loss = total_credit - total_debit
            contents.append([None, 'Verlies', loss, None])
        total = max(total_debit, total_credit)
        contents.append([None, 'Total', total, total])
        return contents

    def _generate_contents_from_balance(self, balance) -> Matrix:
        """
        Generate the contents from a Balance

        :param balance: Balance to export
        :return: Matrix-shaped contents
        """

        header_debit = ['Account', 'Description', 'Debit']
        debit_contents = [header_debit]
        for item in balance.debit_balance_items:
            debit_contents.append([item.account.code, item.account.name, item.value])

        header_debit = ['Account', 'Description', 'Credit']
        credit_contents = [header_debit]
        for item in balance.credit_balance_items:
            credit_contents.append([item.account.code, item.account.name, item.value])

        # Total of debit balance items is by definition equal to total of credit balance items
        total = sum_available_elements([item.value for item in balance.debit_balance_items])
        contents = concatenate_matrices(debit_contents, credit_contents)
        contents.append([None, 'Total', total, None, 'Total', total])
        return contents
