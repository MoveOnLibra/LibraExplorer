from flask import Flask, flash, redirect, render_template, request, session, abort
from flask import jsonify
import werkzeug
import json
import os
import requests
from view_helper import *
import pdb

def is_development():
    try:
        return os.environ["FLASK_ENV"] == "development"
    except Exception:
        return False

def gen_api_header(is_dev, host):
    api_header = {}
    if is_dev:
        suffix = ".localhost:5000"
    else:
        suffix = ".explorer.moveonlibra.com"
    if host.endswith(suffix):
        endlen = -len(suffix)
        api_header["RealSwarm"] = host[0:endlen]
    if is_dev:
        appkey = "eyJhbGciOiJIUzUxMiJ9.eyJkYXRhIjoiZHgxeHl4MnhpIiwiaWF0IjoxNTcyMjUzNTk2LCJleHAiOjE2MDM3ODk1OTZ9.v377ejEaI0oq3KLkT0c8Z3TfF_eTe9LP41RqTcoWyU_fnw2LMhg2ykb3JgoQzJ-1P-qfzHnrgNTHn2PTOs6Bpg"
    else:
        appkey = "eyJhbGciOiJIUzUxMiJ9.eyJkYXRhIjoidHgxeHl4MXh1IiwiaWF0IjoxNTcyOTI0NzQxLCJleHAiOjE2MDQ0NjA3NDF9.2yh_gbH266nWHQ9E_fghs7vVoFHT7a1Z6Zi-NEYt7VTmzK8GPG7BzrBkJ3HATCoVFawss_tLMqqHRUtsGVkJSQ"
    api_header["Authorization"] = f"Bearer {appkey}"
    return api_header

def jwt_header():
    return gen_api_header(is_development(), request.host.lower())


def api_host():
    if is_development():
        return "http://localhost:8000"
    else:
        return "http://apitest.MoveOnLibra.com"

def move_on_libra_api(url, params={}, get_method=True):
    host = api_host()
    try:
        if get_method:
            r = requests.get(host+url, params=params, headers=jwt_header())
        else:
            r = requests.post(host+url, params=params, headers=jwt_header())
    except Exception as err:
        flash(f"Can't finish your request:\n{err}")
        abort(500)
    if r.status_code != 200:
        flash(f"Can't finish your request:\nAPI server return a non 200 response:{r.status_code}\n{r.text}")
        abort(500)
    update_total(int(r.headers["latest_version"])+1)
    data = json.loads(r.content.decode('utf-8-sig'))
    return data

def get_txs(start, limit=10):
    url = "/v1/transactions"
    params = {"limit": limit, "start_version": start}
    return move_on_libra_api(url, params)

def get_latest_txs():
    url = "/v1/transactions/latest"
    params = {"limit": 10}
    return move_on_libra_api(url, params)

def get_transaction(id):
    url = "/v1/transactions/"+str(id)
    return move_on_libra_api(url)


def get_account(address):
    url = "/v1/accounts/"+address
    return move_on_libra_api(url)

def get_account_latest_events(address):
    url = "/v1/accounts/events/latest/"+address
    params = {"limit": 5}
    return move_on_libra_api(url, params)

def post_mint(address):
    url = "/v1/transactions/mint"
    params = {"number_of_micro_libra": 100000000, "receiver_account_address": address}
    return move_on_libra_api(url, params, get_method=False)

def get_validators():
    url = "/v1/libra/validators"
    return move_on_libra_api(url)

def get_metadata():
    url = "/v1/libra/about"
    return move_on_libra_api(url)


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/@MoveOnLibra'
app.config['JSON_SORT_KEYS'] = False

total = 1

def update_total(new_total):
    global total
    total = new_total


@app.route("/")
def index():
    latest_txs = get_latest_txs()
    for tx in latest_txs:
        transaction_format(tx)
    meta = get_metadata()
    format_metadata(meta)
    return render_template('index.html',txs=latest_txs, meta=meta)

@app.route("/transactions")
def transactions():
    start = request.args.get('start', '0')
    txs = get_txs(start)
    for tx in txs:
        transaction_format(tx)
    cur = txs[0]["version"]
    ctx={'first_class': '', 'last_class': ''}
    total_page = total//10
    cur_page = cur//10
    ctx['total'] = total
    ctx['total_page'] = total_page
    ctx['cur_page'] = cur_page
    if cur_page == 0:
        ctx['first_class'] = 'disabled'
    if cur_page == total_page:
        ctx['last_class'] = 'disabled'
    return render_template('transactions.html',txs=txs, ctx=ctx)

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

@app.route("/search")
def search():
    query = request.args.get('q', '')
    if len(query)==64:
        return redirect(f"/accounts/{query}")
    try:
        version = int(query)
        return redirect(f"/transactions/{version}")
    except Exception:
        flash(f"Can't finish your search rquest, maybe the query string '{query}' is malformed.")
        return redirect("/")

@app.errorhandler(werkzeug.exceptions.InternalServerError)
def handle_bad_request(e):
    return render_template('error.html'), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=False)