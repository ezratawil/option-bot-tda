from tda import auth, client
from tda.orders.common import Duration, Session, OrderType
from tda.orders.generic import OrderBuilder
from tda.orders.equities import equity_buy_limit
from tda import auth
import json
import datetime
import os
from chalice import Chalice
from chalicelib import config

app = Chalice(app_name='option-bot')

token_path = os.path.join(os.path.dirname(__file__), 'chalicelib', 'token')
c = auth.client_from_token_file(token_path, config.api_key)


@app.route('/quote/{ticker}')
def quote_ticker(ticker):
    response = c.get_quote(ticker)
    return response.json()

# getting the option chain of a specific security
@app.route('/option/chain/{symbol}')
def option_chain(symbol):
    response = c.get_option_chain(symbol)
    return response.json()

# ordering the option
@app.route('/option/order', methods=['POST'])
def option_order():
    webhook_msg = app.current_request.json_body
    if 'passcode' not in webhook_msg:
        return {
            "code": "error",
            "message": "unauthorized , no passcode"
        }
    if webhook_msg['passcode'] != config.passcode:
        return {
            "code": "error",
            "message": "invalid passcode"
        }

    order_spec = {
        "complexOrderStrategyType": "NONE",
        "orderType": "LIMIT",
        "session": "NORMAL",
        "price": webhook_msg["price"],
        "duration": "DAY",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [
            {
                "instruction": "BUY_TO_OPEN",
                "quantity": webhook_msg["quantity"],
                "instrument": {
                    "symbol": webhook_msg["symbol"],
                    "assetType": "OPTION"
                }
            }
        ]
    }
    response = c.place_order(config.account_id, order_spec)

    return {
        "code": "ok"
    }

