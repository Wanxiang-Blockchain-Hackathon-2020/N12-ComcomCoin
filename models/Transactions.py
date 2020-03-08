from init_params import db
from sqlalchemy import text

class Transactions(db.Model):
    id = db.Column(db.BIGINT, primary_key=True)
    tx_id = db.Column(db.VARCHAR)
    from_account = db.Column(db.VARCHAR)
    to_account = db.Column(db.VARCHAR)
    amount = db.Column(db.BIGINT)
    tx_time = db.Column(db.TIMESTAMP)
    from_account_balances = db.Column(db.BIGINT)
    to_account_balances = db.Column(db.BIGINT)
    pre_tx_id = db.Column(db.VARCHAR)
    from_account_sign = db.Column(db.VARCHAR)
    create_date = db.Column(db.DateTime,default=text('CURRENT_TIMESTAMP'))
    msg = db.Column(db.JSON)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

    def to_bytes4sign(self):
        dict = {}
        dict['from_account'] = self.__dict__['from_account']
        dict['to_account'] = self.__dict__['to_account']
        dict['amount'] = self.__dict__['amount']
        dict['msg'] = self.__dict__['msg']
        dict['tx_time'] = str(self.__dict__['tx_time'])
        dict['pre_tx_id'] = self.__dict__['pre_tx_id'] 
        return bytes('{}'.format(dict), 'utf-8')

    def to_bytes4sha256(self):
        dict = {}
        dict['from_account'] = self.__dict__['from_account']
        dict['to_account'] = self.__dict__['to_account']
        dict['amount'] = self.__dict__['amount']
        dict['msg'] = self.__dict__['msg']
        dict['tx_time'] = self.__dict__['tx_time']
        dict['pre_tx_id'] = self.__dict__['pre_tx_id']
        dict['from_account_balances'] = self.__dict__['from_account_balances']
        dict['to_account_balances'] = self.__dict__['to_account_balances']
        dict['from_account_sign'] = self.__dict__['from_account_sign']

        return bytes('{}'.format(dict), 'utf-8')
