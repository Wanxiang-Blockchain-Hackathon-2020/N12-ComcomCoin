import init_params
from controllers.controller import transact, query_balance_account, create_genesis, verify_tx
from controllers.controller_easy import generate_key,transact_easy,sign

from init_params import app

if __name__ == '__main__':
    app.run()
