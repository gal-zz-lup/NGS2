#!/usr/bin/python
import argparse
import logging
import pandas as pd
import paypalrestsdk as pp
import re


logger = logging.getLogger(__name__)
log_format = '%(asctime)s | %(name)s | %(filename)s (%(lineno)d) | %(levelname)s | %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
logging.getLogger('paypalrestsdk').setLevel(logging.WARN)
logging.getLogger('urllib3').setLevel(logging.INFO)


def batch_size_test(d):
    # ensure no batch has more than 250 entries
    assert d.groupby('batch_id').apply(lambda x: len(x) <= 250).all(), \
    'STOP! Some batches are too large.'


def currency_type_test(d):
    # check currencies are valid
    assert d.currency.all() in ['USD', 'PHP'], \
    'STOP! Not all currency choices are valid.'


def email_formation_test(d):
    EMAIL_CHECK = '^\w*@\w*.(com|org|edu)$'

    # check if email is well-formed
    assert d.receiver_email.apply(lambda x: re.match(EMAIL_CHECK, x)).all(), \
    'STOP! Not all email addresses are well-formed.'


def unique_transaction_ids_test(d):
    # check all item id's are unique
    assert d.groupby('batch_id').item_id.apply(lambda x: len(x) == len(set(x))).all(), \
    'STOP! Not all transactions IDs are unique within batches.'


def values_numeric_test(d):
    # check currency values are valid
    assert d.value.apply(lambda x: isinstance(x, float)).all(), \
    'STOP! Currencies not numeric'


def data_checks(d):
    batch_size_test(d)
    email_formation_test(d)
    values_numeric_test(d)
    currency_type_test(d)
    unique_transaction_ids_test(d)


def build_payout(df):
    return [
        {
            'recipient_type': 'EMAIL',
            'amount': {
                'value': '{0:.2f}'.format(value),
                'currency': currency,
            },
            'receiver': email,
            'note': 'Thank you for playing, we hope you\'ll participate in '
                    'additional experiments.',
            'sender_item_id': item_id,
        } for value, currency, email, item_id in zip(df.value,
                                                     df.currency,
                                                     df.receiver_email,
                                                     df.item_id)
    ]


def run(args_dict):
    # load payout worksheet
    d = pd.read_csv(args_dict['payments'], sep=None, engine='python')

    # run data checks
    data_checks(d)

    # group data by batches
    d = d.groupby('batch_id')

    # authenticate client
    pp.configure(
        {
            'mode': args_dict['environment'],
            'client_id': args_dict['auth'][0],
            'client_secret': args_dict['auth'][1],
        }
    )

    # make payouts
    for batch, details in d:
        payout = pp.Payout(
            {
                'sender_batch_header': {
                    'sender_batch_id': batch,
                    'email_subject': 'Thank you for participating in PROGRAM NAME; '
                                     'here is your incentive payment'
                },
                'items': build_payout(details)
            },
        )

        # send payouts
        if payout.create():
            logger.info('Payout {} successfully processed.'
                        .format(payout.batch_header.payout_batch_id)
            )
        else:
            logger.info(payout.error)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make PayPal payments.')
    parser.add_argument('-a', '--auth', required=True, nargs=2, help='API '
                        'authorization key and secret (in that order).')
    parser.add_argument('-e', '--environment', required=False, default='sandbox',
                        choices=['sandbox', 'production'], help= 'Indicates the '
                        'environment for use.')
    parser.add_argument('-p', '--payments', required=True, help='Path/file to '
                        'CSV with payment information.')
    args_dict = vars(parser.parse_args())

    run(args_dict)
