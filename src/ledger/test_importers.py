import os.path

from datetime import date, datetime
from django.conf import settings
from django.test import TestCase

from common.test_mixins import AccountRequiringMixin
from ledger.importers import LedgerImportError, _parse_contents, _read_xlsx
from ledger.models import Ledger, Transaction


class LedgerImportTestCase(AccountRequiringMixin, TestCase):
    data_dir = os.path.join(settings.BASE_DIR, 'data', 'test', 'importers')
    input_file = os.path.join(data_dir, 'ledger.xlsx')

    ledger_contents = [
        ('ID', 'Date', 'Description', 'Invoice number', 'Contact',
         'Account code', 'Account name', 'Debit', 'Credit'),
        (1, datetime(2018, 1, 1, 0, 0), 'Initial investment', None, None, '1010', 'Bank', 1000, None),
        (None, None, None, None, 'Owner', '2010', 'Creditor: Owner', None, 1000),
        (2, datetime(2018, 1, 2, 0, 0), 'Accountant sent invoice', 'INV-123', None,
         '5010', 'Administration', 300, None),
        (None, None, None, None, 'Accountant', '2011', 'Creditor: Accountant', None, 300),
        (3, datetime(2018, 1, 3, 0, 0), 'Sales', None, None,
         '1010', 'Bank', 400, None),
        (None, None, None, None, None, '4100', 'Sales income', None, 400),
        (4, datetime(2018, 1, 4, 0, 0), 'Partial payment accountant', None, 'Accountant',
         '2011', 'Creditor: Accountant', 200, None),
        (None, None, None, None, None, '1010', 'Bank', None, 200)]

    @property
    def header(self) -> [str]:
        return self.ledger_contents[0]

    def test_that_xlsx_is_properly_read(self):
        contents = list(_read_xlsx(self.input_file))
        expected_contents = self.ledger_contents
        self.assertListEqual(expected_contents, contents)

    def test_that_ledger_import_selects_correct_ledger_per_transaction(self):
        ledger = Ledger.objects.create(year=2018, chart=self.chart)
        contents = [
            self.header,
            [1, datetime(2018, 1, 1, 0, 0), 'Initial investment', None, None, '1010', 'Bank', 1000, None],
            (None, None, None, None, 'Owner', '2010', 'Creditor: Owner', None, 1000),
        ]
        _parse_contents(contents)
        transaction = Transaction.objects.get()
        self.assertEqual(ledger, transaction.ledger)

    def test_that_ledger_import_fills_fields_correctly(self):
        contents = [
            self.header,
            [1, datetime(2018, 1, 1, 0, 0), 'Initial investment', None, None, '1010', 'Bank', 1000, None],
            (None, None, None, None, 'Owner', '2010', 'Creditor: Owner', None, 1000),
        ]
        _parse_contents(contents)
        self.assertEqual(1, Transaction.objects.count())
        transaction = Transaction.objects.get()
        self.assertEqual(date(2018, 1, 1), transaction.date)
        self.assertEqual(Ledger.objects.get(), transaction.ledger)
        self.assertEqual('Initial investment', transaction.description)
        self.assertEqual('', transaction.invoice_number)
        self.assertEqual(self.owner, transaction.contact)
        self.assertEqual(self.bank, transaction.debit_account)
        self.assertEqual(self.creditor_owner, transaction.credit_account)
        self.assertEqual(1000, transaction.amount)

    def test_that_ledger_import_verifies_correct_contact(self):
        contents = [
            self.header,
            [1, datetime(2018, 1, 1, 0, 0), 'Initial investment', None, None, '1010', 'Bank', 1000, None],
            (None, None, None, None, 'Non existing contact', '2010', 'Creditor: Owner', None, 1000),
        ]
        msg = 'Contact with name Non existing contact does not exist'
        with self.assertRaisesMessage(LedgerImportError, msg):
            _parse_contents(contents)

    def test_that_ledger_import_checks_balance_of_transactions(self):
        contents = [
            self.header,
            [1, datetime(2018, 1, 1, 0, 0), 'Initial investment', None, None, '1010', 'Bank', 1000, None],
            (None, None, None, None, 'Owner', '2010', 'Creditor: Owner', None, 1100),
        ]
        msg = 'Transaction in row 3 is not in balance'
        with self.assertRaisesMessage(LedgerImportError, msg):
            _parse_contents(contents)
