import os.path

from common.utils import write_xlsx
from ledger.profit_loss import ProfitLoss

HEADER = ['Account', 'Description', 'Debit', 'Credit']


def write_profit_loss_to_xlsx(profit_loss: ProfitLoss, full_path_to_file: str) -> None:
    """
    Write the given profit loss to an Excel file

    :param profit_loss: ProfitLoss to export
    :param full_path_to_file: Full path to a file
    """

    contents = _generate_contents_from_profit_loss(profit_loss)

    # If the full path to the file does not have an extension, we add the default extension.
    # If it has an extension however, we keep whatever the client passes.
    if os.path.splitext(full_path_to_file)[-1] == '':
        full_path_to_file += '.xlsx'
    write_xlsx(contents, full_path_to_file)


def _generate_contents_from_profit_loss(profit_loss) -> [[str]]:
    """
    Generate the contents from a Profit Loss

    :param profit_loss: ProfitLoss to export
    :return: Matrix-shaped contents
    """

    contents = [HEADER]
    for line in profit_loss.profit_loss_lines:
        contents.append([line.account.code, line.account.name, line.debit, line.credit])
    return contents


def _generate_contents_from_balance(balance) -> [[str]]:
    """
    Generate the contents from a Balance

    :param balance: Balance to export
    :return: Matrix-shaped contents
    """

    contents = [HEADER]
    # TODO: Properly get the contents from a Balance
    for line in balance.debit_balance_items:
        contents.append([line.account_name, line.value_str])
    return contents
