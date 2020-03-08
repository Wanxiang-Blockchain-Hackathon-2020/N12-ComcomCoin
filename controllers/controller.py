from flask import request
from init_params import app
from models.Transactions import Transactions
from datetime import datetime
import hashlib
from sqlalchemy.exc import IntegrityError
import sys
from init_params import db
from sqlalchemy import or_

from ccc_utils.ecc import get_pub_key, get_priv_key, sign, verify_sign, pub_key_str_2_bytes, signature_str_2_bytes, \
    gen_pub_key, gen_priv_key

from exceptions.exceptions import *


@app.route('/create_genesis', methods=['POST'])
def create_genesis():
    res = {}
    res['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        genesis = Transactions()
        genesis.msg = {'declaration ': request.form['declaration'] if 'declaration' in request.form else 'hello world'}
        amount = int(request.form['amount'] if 'amount' in request.form else 1000000000)
        genesis.amount = amount
        genesis.from_account = get_pub_key('pub_genesis.txt', 'string')
        genesis.to_account = get_pub_key('pub.txt', 'string')
        genesis.tx_time = datetime.now()
        genesis.from_account_balances = 0
        genesis.to_account_balances = amount
        genesis.pre_tx_id = '0'
        private_key = get_priv_key('priv_genesis.txt')
        signature = str(int.from_bytes(sign(private_key, genesis.to_bytes4sign()), byteorder='big'))
        assert True == verify_sign(public_key=gen_pub_key(private_key), signature=signature_str_2_bytes(signature),
                                   msg=genesis.to_bytes4sign())
        genesis.from_account_sign = signature
        x = hashlib.sha256()
        x.update(genesis.to_bytes4sha256())
        genesis.tx_id = x.hexdigest()
        db.session.add(genesis)
        db.session.commit()
        res['info'] = 'create_genesis ok'
        res['code'] = '2000'
    except IntegrityError:
        res['info'] = "duplicate entry '0' for key 'pre_tx_id'"
        res['code'] = '1062'
    except:
        res['info'] = "unexpected  error " + str(sys.exc_info()[0])
        res['code'] = '9999'
    return res.__str__()


@app.route('/verify/<tx_id>', methods=['GET'])
def verify_tx(tx_id):
    res = {}
    try:
        transaction = Transactions.query.filter_by(tx_id=tx_id).first()
        pub_key = pub_key_str_2_bytes(transaction.from_account)
        signature = signature_str_2_bytes(transaction.from_account_sign)
        result = verify_sign(public_key=pub_key, signature=signature, msg=transaction.to_bytes4sign())
        res['info'] = 'verify finished'
        res['veriyf'] = result
        res['code'] = '2000'
    except:
        res = {'info': "unexpected  error " + str(sys.exc_info()[0]), 'code': '9999'}
    return res.__str__()


@app.route('/query/balance/<account>', methods=['GET'])
def query_balance_account(account):
    res = {}
    res['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        transaction = Transactions.query.filter(
            or_(Transactions.from_account == account, Transactions.to_account == account)).order_by(
            Transactions.id.desc()).first()
        if transaction is not None:
            if transaction.from_account == account:
                res['balance'] = transaction.from_account_balances
            else:
                res['balance'] = transaction.to_account_balances
            res['info'] = 'query finished'
            res['code'] = '2000'
            res['account'] = account
        else:
            res['info'] = 'no account found'
            res['code'] = '2001'
    except:
        res['info'] = "unexpected  error " + str(sys.exc_info()[0])
        res['code'] = '9999'
    return res.__str__()


@app.route('/query/tx_id/last', methods=['POST'])
def query_tx_id_last():
    res = {}
    res['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        transaction = Transactions.query.order_by(
            Transactions.id.desc()).first()
        res['info'] = 'query ok'
        res['last_tx_id'] = transaction.tx_id
        res['code'] = '2000'
    except:
        res['info'] = "unexpected  error " + str(sys.exc_info()[0])
        res['code'] = '9999'
    return res.__str__()


@app.route('/query/flow/<account>', methods=['GET'])
def query_flow_account(account):
    res = {}
    res['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        transaction_list = Transactions.query.filter(
            or_(Transactions.from_account == account, Transactions.to_account == account)).order_by(
            Transactions.id.desc()).limit(100).all()
        res['info'] = 'query ok'
        tx_list = []
        for tx in transaction_list:
            tx_list.append(tx.to_json())
        res['transactions'] = tx_list
        res['code'] = '2000'
    except:
        res['info'] = "unexpected  error " + str(sys.exc_info()[0])
        res['code'] = '9999'
    return res.__str__()


@app.route('/query/flow/from/<account>/<from_account>', methods=['GET'])
def query_flow_from_account(account, from_account):
    res = {}
    res['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        transaction_list = Transactions.query.filter(Transactions.from_account == from_account,
                                                     Transactions.to_account == account).order_by(
            Transactions.id.desc()).limit(100).all()
        res['info'] = 'query ok'
        tx_list = []
        for tx in transaction_list:
            tx_list.append(tx.to_json())
        res['transactions'] = tx_list
        res['code'] = '2000'
    except:
        res['info'] = "unexpected  error " + str(sys.exc_info()[0])
        res['code'] = '9999'
    return res.__str__()


@app.route('/transact', methods=['POST'])
def transact():
    res = {}
    res['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        transaction = Transactions()
        transaction.msg = {'msg': request.form['declaration'] if 'declaration' in request.form else ''}
        amount = int(request.form['amount'] if 'amount' in request.form else 0)
        transaction.amount = amount
        transaction.from_account = request.form['from_account']
        transaction.to_account = request.form['to_account']
        if transaction.from_account == transaction.to_account:
            raise ValueError
        transaction.tx_time = request.form['tx_time']
        transaction.pre_tx_id = eval(query_tx_id_last())['last_tx_id']
        from_account_balances_last = eval(query_balance_account(transaction.from_account))

        if from_account_balances_last['code'] == '2001':
            raise AccountNoFoundError

        from_account_balances_new = from_account_balances_last['balance'] - amount
        if from_account_balances_new < 0:
            raise BalancesOverflowError

        transaction.from_account_balances = from_account_balances_new
        to_account_balances_last = eval(query_balance_account(transaction.to_account))
        if to_account_balances_last['code'] == '2001':
            to_account_balances_new = amount
        else:
            to_account_balances_new = to_account_balances_last['balance'] + amount
        transaction.to_account_balances = to_account_balances_new

        signature = request.form['signature']

        assert True is verify_sign(public_key=pub_key_str_2_bytes(transaction.from_account),
                                   signature=signature_str_2_bytes(signature),
                                   msg=transaction.to_bytes4sign())
        transaction.from_account_sign = signature
        x = hashlib.sha256()
        x.update(transaction.to_bytes4sha256())
        transaction.tx_id = x.hexdigest()
        db.session.add(transaction)
        db.session.commit()
        res['info'] = 'transaction ok'
        res['code'] = '2000'

    except AccountNoFoundError:
        res['info'] = "from_account no found"
        res['code'] = '2001'

    except BalancesOverflowError:
        res['info'] = "from_account_balances - amount < 0"
        res['code'] = '2002'

    except IntegrityError:
        res['info'] = "duplicate entry " + str(sys.exc_info()[1].args[0])
        res['code'] = '1062'

    except AssertionError:
        res['info'] = "signature match error"
        res['code'] = '2003'

    except ValueError:
        res['info'] = "value error"
        res['code'] = '2004'

    except:
        res['info'] = "unexpected  error " + str(sys.exc_info()[0])
        res['code'] = '9999'
    return res.__str__()


@app.route('/transact/batch', methods=['POST'])
def transact_batch():
    res = {}
    res['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        transaction = Transactions()
        transaction.msg = {'msg': request.form['declaration'] if 'declaration' in request.form else ''}
        amount = int(request.form['amount'] if 'amount' in request.form else 0)
        transaction.amount = amount
        transaction.from_account = request.form['from_account']
        transaction.to_account = request.form['to_account']
        transaction.tx_time = request.form['tx_time']
        from_account_balances_last = eval(query_balance_account(transaction.from_account))

        if from_account_balances_last['code'] == '2001':
            raise AccountNoFoundError

        from_account_balances_new = from_account_balances_last['balance'] - amount
        if from_account_balances_new < 0:
            raise BalancesOverflowError

        transaction.from_account_balances = from_account_balances_new
        to_account_balances_last = eval(query_balance_account(transaction.to_account))
        if to_account_balances_last['code'] == '2001':
            to_account_balances_new = amount
        else:
            to_account_balances_new = to_account_balances_last['balance'] + amount
        transaction.to_account_balances = to_account_balances_new
        transaction.pre_tx_id = eval(query_tx_id_last())['last_tx_id']

        signature = request.form['signature']

        assert True is verify_sign(public_key=pub_key_str_2_bytes(transaction.from_account),
                                   signature=signature_str_2_bytes(signature),
                                   msg=transaction.to_bytes4sign())
        transaction.from_account_sign = signature
        x = hashlib.sha256()
        x.update(transaction.to_bytes4sha256())
        transaction.tx_id = x.hexdigest()
        db.session.add(transaction)

        transaction2 = Transactions()
        transaction2.msg = {'msg': request.form['declaration'] if 'declaration' in request.form else ''}
        amount = int(request.form['amount'] if 'amount' in request.form else 0)
        transaction2.amount = amount
        transaction2.from_account = request.form['from_account']
        transaction2.to_account = request.form['to_account']
        transaction2.tx_time = request.form['tx_time']
        from_account_balances_last = eval(query_balance_account(transaction2.from_account))

        if from_account_balances_last['code'] == '2001':
            raise AccountNoFoundError

        from_account_balances_new = from_account_balances_last['balance'] - amount
        if from_account_balances_new < 0:
            raise BalancesOverflowError

        transaction2.from_account_balances = from_account_balances_new
        to_account_balances_last = eval(query_balance_account(transaction2.to_account))
        if to_account_balances_last['code'] == '2001':
            to_account_balances_new = amount
        else:
            to_account_balances_new = to_account_balances_last['balance'] + amount
        transaction2.to_account_balances = to_account_balances_new
        transaction2.pre_tx_id = eval(query_tx_id_last())['last_tx_id']

        signature = request.form['signature']

        assert True is verify_sign(public_key=pub_key_str_2_bytes(transaction2.from_account),
                                   signature=signature_str_2_bytes(signature),
                                   msg=transaction2.to_bytes4sign())
        transaction2.from_account_sign = signature
        x = hashlib.sha256()
        x.update(transaction2.to_bytes4sha256())
        transaction2.tx_id = x.hexdigest()

        db.session.add(transaction2)
        db.session.commit()
        res['info'] = 'transaction ok'
        res['code'] = '2000'

    except IntegrityError:
        res['info'] = "duplicate entry " + str(sys.exc_info()[1].args[0])
        res['code'] = '1062'
        db.session.rollback()

    except AssertionError:
        res['info'] = "signature match error"
        res['code'] = '2003'
        db.session.rollback()

    except ValueError:
        res['info'] = "value error"
        res['code'] = '2004'
        db.session.rollback()

    except AccountNoFoundError:
        res['info'] = "from_account no found"
        res['code'] = '2001'

    except BalancesOverflowError:
        res['info'] = "from_account_balances - amount < 0"
        res['code'] = '2002'
    except:
        res['info'] = "unexpected  error " + str(sys.exc_info()[0])
        res['code'] = '9999'
        db.session.rollback()

    return res.__str__()
