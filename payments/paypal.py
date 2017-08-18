#!/usr/bin/python
import argparse
import logging
import pandas as pd
import paypalrestsdk as pp
import re
import sys


logger = logging.getLogger(__name__)
log_format = '%(asctime)s | %(name)s | %(filename)s (%(lineno)d) | %(levelname)s | %(message)s'
logging.basicConfig(filename='payments/paypal_processing.log', format=log_format,
                    level=logging.DEBUG)
logging.getLogger('paypalrestsdk').setLevel(logging.WARN)
logging.getLogger('urllib3').setLevel(logging.INFO)


def data_structure_test(d):
    # ensure all expected columns and no others are present
    EXPECTED_COLUMNS = {
        'batch_id',
        'currency',
        'first_name',
        'item_id',
        'processed_code',
        'receiver_email',
        'value'
    }
    assert set(d.columns) == EXPECTED_COLUMNS, \
    'STOP! The input worksheet is not structured as expected.'


def batch_size_test(d):
    # ensure no batch has more than 250 entries
    assert d.groupby('batch_id').apply(lambda x: len(x) <= 500).all(), \
    'STOP! Some batches are too large.'


def check_name_test(d):
    # check that names are not missing and place in proper case
    assert d.first_name.notnull().all(), \
    'STOP! Some names are missing.'
    return d.first_name.apply(lambda x: x.title())


def currency_type_test(d):
    # check currencies are valid
    d.currency = d.currency.apply(lambda x: x.upper())
    assert d.currency.all() in ['USD', 'PHP'], \
    'STOP! Not all currency choices are valid.'
    return d.currency


def email_formation_test(d):
    # check if email is well-formed
    EMAIL_CHECK = '^\w*@\w*.(com|org|edu)$'
    assert d.receiver_email.apply(lambda x: re.match(EMAIL_CHECK, x)).all(), \
    'STOP! Not all email addresses are well-formed.'


def unique_transaction_ids_test(d):
    # check all item id's are unique
    assert d.groupby('batch_id').item_id.apply(lambda x: len(x) == len(set(x))).all(), \
    'STOP! Not all transactions IDs are unique within batches.'


def values_numeric_test(d):
    # check currency values are valid
    assert d.value.apply(lambda x: isinstance(x, (int, float))).all(), \
    'STOP! Currencies not numeric'


def data_checks(d):
    data_structure_test(d)
    batch_size_test(d)
    d.first_name = check_name_test(d)
    email_formation_test(d)
    values_numeric_test(d)
    d.currency = currency_type_test(d)
    unique_transaction_ids_test(d)


def build_payout(df):
    MESSAGES = [('Greetings {}. Thank you for participating in the World Lab. If '
               'you have any problems retrieving your incentive payment, please '
               'contact World_Lab@gallup.com. We look forward to offering '
               'you additional World Lab opportunities in '
               'the future.'.format(name)) for name in df.first_name]
    return [
        {
            'recipient_type': 'EMAIL',
            'amount': {
                'value': '{0:.2f}'.format(value),
                'currency': currency,
            },
            'receiver': email,
            'note': message,
            'sender_item_id': item_id,
        } for message, value, currency, email, item_id in zip(MESSAGES,
                                                              df.value,
                                                              df.currency,
                                                              df.receiver_email,
                                                              df.item_id)
    ]


def run(args_dict):
    # start logger
    logger.info('Starting transactions for {}.'.format(args_dict['payments']))

    # load payout worksheet
    d = pd.read_csv(args_dict['payments'], sep=None, engine='python')

    # subset to new transactions
    subd = d[d.processed_code.isnull()]
    if subd.shape[0]==0:
        logger.info('STOP! No new transactions to process. Quitting and closing log.\n')
        sys.exit()

    # run data checks
    data_checks(subd)

    # group data by batches
    subd = subd.groupby('batch_id')

    # authenticate client
    pp.configure(
        {
            'mode': args_dict['environment'],
            'client_id': args_dict['auth'][0],
            'client_secret': args_dict['auth'][1],
        }
    )

    # make payouts
    for batch, details in subd:
        payout = pp.Payout(
            {
                'sender_batch_header': {
                    'sender_batch_id': batch,
                    'email_subject': 'World Lab Incentive Payment'
                },
                'items': build_payout(details)
            },
        )

        # send payouts
        if payout.create():
            logger.info('Payout for `batch_id` {} successfully processed '
                        '(processing code: {}).'
                        .format(batch, payout.batch_header.payout_batch_id)
            )
            d.loc[(d.batch_id==batch) & (d.processed_code.isnull()),
                  'processed_code'] = payout.batch_header.payout_batch_id
        else:
            logger.info(payout.error)

    # output data
    d.to_csv(args_dict['payments'], index=False)
    logger.info('Closing log for {}.\n'.format(args_dict['payments']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make PayPal payments.')
    parser.add_argument('-a', '--auth', required=True, nargs=2, help='API '
                        'authorization key and secret (in that order).')
    parser.add_argument('-e', '--environment', required=False, default='sandbox',
                        choices=['sandbox', 'live'], help= 'Indicates the '
                        'environment for use.')
    parser.add_argument('-p', '--payments', required=True, help='Path/file to '
                        'CSV with payment information.')
    args_dict = vars(parser.parse_args())

    run(args_dict)
