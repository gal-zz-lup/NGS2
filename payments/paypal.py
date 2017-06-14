#!/usr/bin/python
import argparse
import os
import requests

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


class PayPal(object):
    AUTH_EP = 'v1/oauth2/token'
    PAYMENTS_EP = 'v1/payments'

    def __init__(self, args_dict):
        self.HOST = self.resolve_host(args_dict['environment'])
        self.key = args_dict['key']
        self.secret = args_dict['secret']
        self.token = None

    def resolve_host(self, host):
        if host == 'sandbox':
            return 'https://api.sandbox.paypal.com'
        else:
            return 'https://api.paypal.com'

    def authenticate(self):
        client = BackendApplicationClient(client_id=self.key)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url='{}/{}'.format(self.HOST, self.AUTH_EP),
                                  client_id=self.key, client_secret=self.secret)
        self.token = token['access_token']

    def get_sale(self, sale):
        URL = '{}/{}/sale/{}'.format(self.HOST, self.PAYMENTS_EP, sale)
        r = requests.get(
            URL,
            # headers={
            #     'Content-Type': 'application/json',
            #     'Authorization': 'Bearer {}'.format(self.token),
            # },
            # params = {
            #     'sale_id': sale,
            # }
        )
        return r

    def make_payment(self, intent, payer, transactions, redirect_urls=None):
        URL = '{}/{}/payment'.format(self.HOST, self.PAYMENTS_EP)
        r = requests.post(
            URL,
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.token),
            },
            params = {
                "intent": intent,
                "redirect_urls": literal_eval(redirect_urls),
                "payer": literal_eval(payer),
                "transactions": literal_eval(transactions),
            }
        )
        return r

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make PayPal payments.')
    parser.add_argument('-e', '--environment', required=False, default='sandbox',
                        choices=['sandbox', 'production'], help= 'Indicates the '
                        'environment for use.')
    parser.add_argument('-k', '--key', required=True, help='API authorization key.')
    parser.add_argument('-s', '--secret', required=True, help='API authorization '
                        'secret.')
