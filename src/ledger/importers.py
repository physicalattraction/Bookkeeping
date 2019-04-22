from openpyxl import load_workbook

from accounts.models import Account, ChartOfAccounts
from common.utils import Matrix
from contacts.models import Contact
from ledger.models import Transaction, Ledger


class LedgerImportError(Exception):
    pass


def import_transactions_from_xlsx(full_path_to_file: str) -> None:
    contents = _read_xlsx(full_path_to_file)
    _parse_contents(contents)


def _read_xlsx(full_path_to_file: str) -> Matrix:
    """
    Read an Excel file with one sheet and return the contents as a Matrix
    """

    workbook = load_workbook(filename=full_path_to_file, read_only=True)
    worksheet = workbook.active
    return list(worksheet.values)


def _parse_contents(contents: Matrix):
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
            if transaction:
                transaction.save()
            transaction = Transaction()

        transaction_date = row[header.index('Date')]
        if transaction_date:
            transaction.date = transaction_date
            transaction.ledger, _ = Ledger.objects.get_or_create(year=transaction.date.year, chart=chart)
        transaction.description = row[header.index('Description')] or transaction.description
        transaction.invoice_number = row[header.index('Invoice number')] or transaction.invoice_number

        # Fetch the correct contact
        contact_name = row[header.index('Contact')]
        try:
            if contact_name:
                transaction.contact = Contact.objects.get(name=contact_name)
        except Contact.DoesNotExist:
            # TODO: Create on the spot with input from user?
            msg = 'Contact with name {} does not exist'.format(contact_name)
            raise LedgerImportError(msg)

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
    if transaction:
        transaction.save()
