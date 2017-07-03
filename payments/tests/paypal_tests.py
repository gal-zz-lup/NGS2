#!/usr/bin/python
import numpy as np
import pandas as pd
import pytest

from NGS2.payments.paypal import *


@pytest.mark.parametrize('test', [
    (pd.DataFrame({'batch_id': ['A', 'A', 'B']})),
])
def test_batch_size_test_pass(test):
    assert batch_size_test(test) == None


@pytest.mark.parametrize('test', [
    (pd.DataFrame({'batch_id': np.repeat('long', 251)})),
])
@pytest.mark.xfail(raises=AssertionError)
def test_batch_size_test_fail(test):
    assert batch_size_test(test)


@pytest.mark.parametrize('test', [
    (pd.DataFrame({'currency': ['USD', 'PHP', 'USD']})),
])
def test_currency_type_test_pass(test):
    assert currency_type_test(test) == None


@pytest.mark.parametrize('test', [
    (pd.DataFrame({'currency': ['USD', 'US', 'AUD']})),
])
@pytest.mark.xfail(raises=AssertionError)
def test_currency_type_test_fail(test):
    assert currency_type_test(test)


@pytest.mark.parametrize('test', [
    (pd.DataFrame({
        'receiver_email': ['this@g.com', 'that@help.edu', '112@test.org']
    })),
])
def test_email_formation_test_pass(test):
    assert email_formation_test(test) == None


@pytest.mark.parametrize('test', [
    (pd.DataFrame({
        'receiver_email': ['112@help', 'this@good.com', 'that#fail.org']
    })),
])
@pytest.mark.xfail(raises=AssertionError)
def test_email_formation_test_fail(test):
    assert email_formation_test(test)


@pytest.mark.parametrize('test', [
    (pd.DataFrame({
        'batch_id': ['A', 'A', 'B'],
        'item_id': [1, 2, 1],
    })),
])
def test_unique_transaction_ids_test_pass(test):
    assert unique_transaction_ids_test(test) == None


@pytest.mark.parametrize('test', [
    (pd.DataFrame({
        'batch_id': ['A', 'A', 'B'],
        'item_id': [1, 1, 1],
    })),
])
@pytest.mark.xfail(raises=AssertionError)
def test_unique_transaction_ids_test_fail(test):
    assert unique_transaction_ids_test(test)


@pytest.mark.parametrize('test', [
    (pd.DataFrame({'value': [1, .99, 2.3, 14]})),
])
def test_values_numeric_test_pass(test):
    assert values_numeric_test(test) == None


@pytest.mark.parametrize('test', [
    (pd.DataFrame({'value': ['1', '1.99', 2.3, 14]})),
])
@pytest.mark.xfail(raises=AssertionError)
def test_values_numeric_test_fail(test):
    assert values_numeric_test(test)


@pytest.mark.parametrize('test, expected', [
    (pd.DataFrame({
        'value': [1],
        'currency': ['USD'],
        'receiver_email': ['this@test.com'],
        'item_id': ['A'],
    }), ('1.00', 'USD', 'this@test.com', 'A')),
    (pd.DataFrame({
        'value': [199.34],
        'currency': ['PHP'],
        'receiver_email': ['that@test.org'],
        'item_id': ['B'],
    }), ('199.34', 'PHP', 'that@test.org', 'B')),
    (pd.DataFrame({
        'value': [.5],
        'currency': ['USD'],
        'receiver_email': ['t@t.edu'],
        'item_id': ['C'],
    }), ('0.50', 'USD', 't@t.edu', 'C')),
])
def test_build_payout(test, expected):
    result = build_payout(test)
    assert result[0]['amount']['value'] == expected[0]
    assert result[0]['amount']['currency'] == expected[1]
    assert result[0]['receiver'] == expected[2]
    assert result[0]['sender_item_id'] == expected[3]
