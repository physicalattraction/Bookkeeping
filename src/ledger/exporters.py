import os.path

from common.utils import Matrix, concatenate_matrices, write_xlsx
from ledger.balance import Balance
from ledger.profit_loss import ProfitLoss


def write_profit_loss_to_xlsx(profit_loss: ProfitLoss, full_path_to_file: str) -> None:
    """
    Write the given profit loss to an Excel file

    :param profit_loss: ProfitLoss to export
    :param full_path_to_file: Full path to a file
    """

    contents = _generate_contents_from_profit_loss(profit_loss)


    write_xlsx(contents, full_path_to_file)


def write_balance_to_xlsx(balance: Balance, full_path_to_file: str) -> None:
    """
    Write the given balance to an Excel file

    :param balance: Balance to export
    :param full_path_to_file: Full path to a file
    """

    contents = _generate_contents_from_balance(balance)
    write_xlsx(contents, full_path_to_file)


def write_profit_loss_and_balance_to_xlsx(profit_loss: ProfitLoss, balance: Balance, full_path_to_file: str) -> None:
    """
    Write the given profit loss and balance to an Excel file, each in a separate worksheet

    :param profit_loss: ProfitLoss to export
    :param full_path_to_file: Full path to a file
    """

    profit_loss_contents = _generate_contents_from_profit_loss(profit_loss)
    if os.path.splitext(full_path_to_file)[-1] == '':
        full_path_to_file += '.xlsx'
    workbook = write_xlsx(profit_loss_contents, full_path_to_file, worksheet_name='PL')

    balance_contents = _generate_contents_from_balance(balance)
    write_xlsx(balance_contents, full_path_to_file, workbook=workbook, worksheet_name='Balance')


def _generate_contents_from_profit_loss(profit_loss) -> [[str]]:
    """
    Generate the contents from a Profit Loss

    :param profit_loss: ProfitLoss to export
    :return: Matrix-shaped contents
    """

    header = ['Account', 'Description', 'Debit', 'Credit']
    contents = [header]
    for line in profit_loss.profit_loss_lines:
        contents.append([line.account.code, line.account.name, line.debit, line.credit])

    # TODO: Add total lines
    return contents


def _generate_contents_from_balance(balance) -> Matrix:
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

    # TODO: Add total lines
    return concatenate_matrices(debit_contents, credit_contents)
