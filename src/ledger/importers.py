from datetime import date

from typing import Optional

from openpyxl import load_workbook

from accounts.models import Account, ChartOfAccounts
from common.utils import Matrix
from contacts.models import Contact
from ledger.models import Ledger, Transaction


class LedgerImportError(Exception):
    pass


class LedgerImporter:
    def __init__(self):
        self.transactions = list(Transaction.objects.all())

    def import_transactions_from_xlsx(self, full_path_to_file: str) -> None:
        contents = self._read_xlsx(full_path_to_file)
        self._parse_contents(contents)

    def _read_xlsx(self, full_path_to_file: str) -> Matrix:
        """
        Read an Excel file with one sheet and return the contents as a Matrix
        """

        workbook = load_workbook(filename=full_path_to_file, read_only=True)
        worksheet = workbook.active
        return list(worksheet.values)

    def _parse_contents(self, contents: Matrix):
        """
        Create transactions from the given input data
        """

        chart = ChartOfAccounts.objects.get()
        header = contents.pop(0)
        transaction = None
        for index, row in enumerate(contents, start=2):  # Row 1 = header, row 2 = first data row
            if row[header.index('ID')] is None:
                assert transaction is not None
            else:
                # A new transaction is started. Save the old one and start a new one.
                self._save_transaction(transaction)
                transaction = Transaction()

            transaction_datetime = row[header.index('Date')]
            if transaction_datetime:
                transaction.date = transaction_datetime.date()
            transaction.description = row[header.index('Description')] or transaction.description
            transaction.invoice_number = row[header.index('Invoice number')] or transaction.invoice_number

            # Fetch the correct contact
            contact_name = row[header.index('Contact')]
            if contact_name:
                transaction.contact, _ = Contact.objects.get_or_create(name=contact_name)

            # Fetch the correct account
            account_code = row[header.index('Account code')]
            try:
                account = Account.objects.get(chart=chart, code=account_code)
            except Account.DoesNotExist as e:
                msg = 'Account with code {} does not exist'.format(account_code)
                raise LedgerImportError(msg) from e

            debit_amount = row[header.index('Debit')]
            credit_amount = row[header.index('Credit')]
            if debit_amount is not None:
                assert credit_amount is None, 'Row {} has a debit and a credit amount set'.format(index)
                transaction.debit_account = account
                if transaction.amount:
                    if transaction.amount != debit_amount:
                        msg = 'Transaction in row {} is not in balance'.format(index)
                        raise LedgerImportError(msg)
                else:
                    transaction.amount = debit_amount
            elif credit_amount is not None:
                transaction.credit_account = account
                if transaction.amount:
                    if transaction.amount != credit_amount:
                        msg = 'Transaction in row {} is not in balance'.format(index)
                        raise LedgerImportError(msg)
                else:
                    transaction.amount = credit_amount
            else:
                msg = 'Row {} has neither a debit nor a credit amount set'.format(index)
                raise LedgerImportError(msg)

        # Save the last transaction
        self._save_transaction(transaction)

    def _save_transaction(self, transaction: Optional[Transaction]):
        """
        Update or create the current transaction
        """

        if not transaction:
            return

        transaction.clean()
        # TODO: Bulk create transactions
        existing_transaction = next((t for t in self.transactions if t == transaction), None)
        if existing_transaction:
            existing_transaction.delete()
        transaction.save()
        self.transactions.append(transaction)