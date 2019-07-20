from django.core.management import BaseCommand
from django.utils import timezone

from accounts.models import Account, ChartOfAccounts

# https://www.administratievoeren.nl/grootboekrekeningschema/
from ledger.models import Transaction, Ledger

DEBIT_PROFIT_LOSS_ACCOUNTS = {
    '4700': 'Rente lening u/g',
    '4720': 'Rente bank',
    '4790': 'Overige rentebaten',
    '4990': 'Overige baten',

    '8000': 'Omzet',

    '9000': 'Resultaat deelneming',
    '9800': 'Betalingskorting inkoop',
}

CREDIT_PROFIT_LOSS_ACCOUNTS = {
    '4000': 'Lonen en salarissen',
    '4005': 'Vakantiegeld',
    '4020': 'Uitkering ziekengeld',
    '4030': 'Sociale lasten',
    '4035': 'Pensioenpremies',
    '4040': 'Uitzendkrachten',
    '4045': 'Managementvergoeding',
    '4050': 'Kantinekosten',
    '4051': 'Bedrijfskleding',
    '4052': 'Congressen',
    '4053': 'Opleidingskosten',
    '4060': 'Reiskosten',
    '4090': 'Overige personeelskosten',
    '4100': 'Huur gebouwen en terreinen',
    '4105': 'Onderhoud gebouwen en terreinen',
    '4110': 'Dotatie voorziening groot onderhoud',
    '4120': 'Gas / water / licht',
    '4125': 'Schoonmaakkosten',
    '4130': 'Assurantie gebouwen en terreinen',
    '4190': 'Overige huisvestingskosten',
    '4200': 'Huur machines',
    '4210': 'Lease machines',
    '4220': 'Onderhoud machines',
    '4290': 'Overige exploitatiekosten',
    '4300': 'Contributies en abonnementen',
    '4310': 'Kantoorbenodigdheden',
    '4320': 'Telefoonkosten',
    '4330': 'Porti',
    '4340': 'Overige kantoorkosten',
    '4400': 'Brandstoffen',
    '4410': 'Lease vervoermiddelen',
    '4420': 'Onderhoud vervoermiddelen',
    '4440': 'Assuranties vervoermiddelen',
    '4450': 'Wegenbelasting',
    '4460': 'Privé gebruik auto\'s',
    '4500': 'Reclame- en advertentiekosten',
    '4510': 'Reis- en verblijfkosten',
    '4520': 'Representatiekosten',
    '4530': 'Beurskosten',
    '4590': 'Overige verkoopkosten',
    '4600': 'Accountantskosten',
    '4610': 'Advieskosten',
    '4620': 'Notariskosten',
    '4630': 'Juridische kosten',
    '4640': 'Bankkosten',
    '4650': 'Verzekeringen',
    '4660': 'Kosten deelnemingen',
    '4690': 'Overige algemene kosten',
    '4710': 'Rente lening o/g',
    '4730': 'Rente lease',
    '4795': 'Overige rentelasten',
    '4800': 'Afschrijving gebouwen',
    '4810': 'Afschrijving inventaris',
    '4820': 'Afschrijving machines en installaties',
    '4830': 'Afschrijving vervoermiddelen',
    '4890': 'Boekresultaat vaste activa',
    '4900': 'Kleine ondernemersregeling btw',
    '4910': 'Koersverschillen',
    '4920': 'Kasverschillen',
    '4995': 'Overige lasten',

    '7000': 'Inkoopwaarde van de omzet',

    '9810': 'Betalingskorting verkoop',
    '9900': 'Vennootschapsbelasting',
    '9999': 'Resultaat'
}

DEBIT_BALANCE_ACCOUNTS = {
    '0010': 'Goodwill',
    '0015': 'Afschrijving goodwill',
    '0050': 'Gebouwen en terreinen',
    '0055': 'Afschrijving gebouwen en terreinen',
    '0060': 'Machines en installaties',
    '0065': 'Afschrijving machines en installaties',
    '0070': 'Inventaris',
    '0075': 'Afschrijving inventaris',
    '0080': 'Vervoermiddelen',
    '0085': 'Afschrijving vervoermiddelen',
    '0500': 'Deelneming',
    '0501': 'Aandelen Nyon Business BV',
    '0502': 'Aandelen 922 AM BV',
    '0503': 'Aandelen Nyon Holding BV',
    '0600': 'Aandelenkapitaal',
    '0605': 'Wettelijke reserve',
    '0610': 'Algemene reserve',
    '0690': 'Winstsaldo',
    '0800': 'Voorzieningen',
    '0900': 'Lening o/g',

    '1000': 'Kas',
    '1100': 'Bank',
    '1300': 'Debiteuren',
    '1301': 'Debiteuren: 922 AM BV',
    '1400': 'Te vorderen',
    '1520': 'Te vorderen BTW 21%',
    '1530': 'Te vorderen BTW 6%',
    '1650': 'Dividend',

    '2900': 'Betalingen onderweg',

    '3000': 'Voorraad',
    '3100': 'Onderhanden werk'
}

CREDIT_BALANCE_ACCOUNTS = {
    '1500': 'Af te dragen BTW 21%',
    '1510': 'Af te dragen BTW 9%',
    '1540': 'BTW te betalen',
    '1550': 'BTW betaald',
    '1600': 'Crediteuren',
    '1601': 'Crediteuren: Erwin',
    '1602': 'Crediteuren: KvK',
    '1603': 'Crediteuren: AMBH',
    '1604': 'Crediteuren: Nyon Holding BV',
    '1670': 'Dividendbelasting',
    '1680': 'Vennootschapsbelasting',
    '1700': 'Te betalen',
    '1800': 'Rekening-courant',

    '2000': 'Kruisposten',

}


class Command(BaseCommand):
    help = 'Generate a default set of Accounts in a single ChartOfAccounts'

    def handle(self, *args, **options):
        if options['force']:
            Ledger.objects.all().delete()  # Cascades to transactions which hold references to Accounts
            ChartOfAccounts.objects.all().delete()

        # TODO: Once there are multiple charts of accounts possible, make this an input argument
        #       Also at that moment, make a possibility to add them to an existing Chart of Accounts
        chart = ChartOfAccounts.objects.create()

        now = timezone.now()
        accounts = [Account(uuid=Account.generate_uuid(), created_at=now, updated_at=now,
                            chart=chart, code=code, name=name, type=Account.PROFIT_LOSS, debit_type=Account.DEBIT)
                    for code, name in DEBIT_PROFIT_LOSS_ACCOUNTS.items()]
        accounts += [Account(uuid=Account.generate_uuid(), created_at=now, updated_at=now,
                             chart=chart, code=code, name=name, type=Account.PROFIT_LOSS, debit_type=Account.CREDIT)
                     for code, name in CREDIT_PROFIT_LOSS_ACCOUNTS.items()]
        accounts += [Account(uuid=Account.generate_uuid(), created_at=now, updated_at=now,
                             chart=chart, code=code, name=name, type=Account.BALANCE, debit_type=Account.DEBIT)
                     for code, name in DEBIT_BALANCE_ACCOUNTS.items()]
        accounts += [Account(uuid=Account.generate_uuid(), created_at=now, updated_at=now,
                             chart=chart, code=code, name=name, type=Account.BALANCE, debit_type=Account.CREDIT)
                     for code, name in CREDIT_BALANCE_ACCOUNTS.items()]
        Account.objects.bulk_create(accounts)

    def add_arguments(self, parser):
        help_force = 'Force the deletion and creation of all Accounts by deleting the associated transactions as well'
        parser.add_argument('--force', dest='force', action='store_true', default=False,
                            help=help_force)
