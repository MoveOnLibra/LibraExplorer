from flask import Flask, flash, redirect, render_template, request, session, abort
from flask import jsonify
import json
import requests
from view_helper import *
import pdb

def jwt_header():
    appkey = "eyJhbGciOiJIUzUxMiJ9.eyJkYXRhIjoiZHgxeHl4MnhpIiwiaWF0IjoxNTcyMjUzNTk2LCJleHAiOjE2MDM3ODk1OTZ9.v377ejEaI0oq3KLkT0c8Z3TfF_eTe9LP41RqTcoWyU_fnw2LMhg2ykb3JgoQzJ-1P-qfzHnrgNTHn2PTOs6Bpg"
    return {"Authorization": f"Bearer {appkey}"}

def get_txs(start, limit=10):
    url = "http://localhost:8000/v1/transactions"
    params = {"limit": limit, "start_version": start}
    r = requests.get(url, params=params, headers=jwt_header())
    if r.status_code != 200:
        return _('Error: the service failed.')
    data = json.loads(r.content.decode('utf-8-sig'))
    return data

def get_latest_txs():
    url = "http://localhost:8000/v1/transactions/latest"
    params = {"limit": 10}
    r = requests.get(url, params=params, headers=jwt_header())
    if r.status_code != 200:
        return _('Error: the service failed.')
    data = json.loads(r.content.decode('utf-8-sig'))
    return data

def get_transaction(id):
    url = "http://localhost:8000/v1/transactions/"+str(id)
    r = requests.get(url, headers=jwt_header())
    if r.status_code != 200:
        return _('Error: the service failed.')
    data = json.loads(r.content.decode('utf-8-sig'))
    return data


def get_account(address):
    url = "http://localhost:8000/v1/accounts/"+address
    r = requests.get(url, headers=jwt_header())
    if r.status_code != 200:
        return _('Error: the service failed.')
    data = json.loads(r.content.decode('utf-8-sig'))
    return data

def get_account_latest_events(address):
    url = "http://localhost:8000/v1/accounts/events/latest/"+address
    params = {"limit": 5}
    r = requests.get(url, params=params, headers=jwt_header())
    if r.status_code != 200:
        return _('Error: the service failed.')
    data = json.loads(r.content.decode('utf-8-sig'))
    return data

def post_mint(address):
    url = "http://localhost:8000/v1/transactions/mint"
    params = {"number_of_micro_libra": 100000000, "receiver_account_address": address}
    r = requests.post(url, params=params, headers=jwt_header())
    #pdb.set_trace()
    if r.status_code != 200:
        return _('Error: the service failed.')
    return r

def get_validators():
    url = "http://localhost:8000/v1/libra/validators"
    r = requests.get(url, headers=jwt_header())
    if r.status_code != 200:
        return _('Error: the service failed.')
    data = json.loads(r.content.decode('utf-8-sig'))
    return data

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

latest_txs = None

@app.route("/")
def index():
    global latest_txs
    if latest_txs is None:
        pass
    latest_txs = get_latest_txs()
    for tx in latest_txs:
        transaction_format(tx)
    return render_template('index.html',txs=latest_txs)

@app.route("/transactions")
def transactions():
    start = request.args.get('start', '0')
    txs = get_txs(start)
    for tx in txs:
        transaction_format(tx)
    return render_template('transactions.html',txs=txs)

@app.route("/transactions/<int:id>")
def transaction(id):
    tx = get_transaction(id)
    raw_json = json.dumps(tx, indent=2)
    transaction_format(tx)
    tx['raw_json'] = raw_json
    #TODO: 404
    return render_template('transaction_show.html',tx=tx)

@app.route("/transactions/<int:id>.json")
def transaction_json(id):
    tx = get_transaction(id)
    return jsonify(tx)

@app.route("/accounts")
def accounts():
    validators = get_validators()
    return render_template('accounts.html', validators=enumerate(validators),
        core_code_address='0000000000000000000000000000000000000000000000000000000000000000',
        association_address='000000000000000000000000000000000000000000000000000000000a550c18',
        transaction_fee_address='0000000000000000000000000000000000000000000000000000000000000fee',
        validator_set_address='00000000000000000000000000000000000000000000000000000000000001d8'
        )


@app.route("/accounts/<string:address>")
def account(address):
    acc = get_account(address)
    raw_json = json.dumps(acc, indent=2)
    try:
        events = get_account_latest_events(address)
        for ev in events['sent']:
            event_format(ev)
        for ev in events['received']:
            event_format(ev)
        acc['events'] = events
    except Exception:
        #TODO: Request failed DB corrupt: Sequence number not continuous, expected: 0, actual: 1.
        acc['events'] = {'sent':[], 'received':[]}
    acc['raw_json'] = raw_json
    #TODO: 404
    return render_template('account_show.html',acc=acc)


@app.route("/accounts/<string:address>.json")
def account_json(address):
    acc = get_account(address)
    return jsonify(acc)


@app.route("/transactions/mint/<string:address>", methods=['POST'])
def mint(address):
    post_mint(address)
    return redirect(f"/accounts/{address}")

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=False)