from flask import Flask, flash, redirect, render_template, request, session, abort
from flask import jsonify
import json
import requests
from view_helper import *
import pdb


def get_latest_txs():
    appid = "00002"
    appkey = "eyJhbGciOiJIUzUxMiJ9.eyJkYXRhIjoiZHgxeHl4MnhpIiwiaWF0IjoxNTcyMjUzNTk2LCJleHAiOjE2MDM3ODk1OTZ9.v377ejEaI0oq3KLkT0c8Z3TfF_eTe9LP41RqTcoWyU_fnw2LMhg2ykb3JgoQzJ-1P-qfzHnrgNTHn2PTOs6Bpg"
    url = "http://localhost:8000/v1/transactions/latest?limit=10&appid="+appid+"&appkey="+appkey
    r = requests.get(url)
    if r.status_code != 200:
        return _('Error: the service failed.')
    data = json.loads(r.content.decode('utf-8-sig'))
    return data

def get_transaction(id):
    appid = "00002"
    appkey = "eyJhbGciOiJIUzUxMiJ9.eyJkYXRhIjoiZHgxeHl4MnhpIiwiaWF0IjoxNTcyMjUzNTk2LCJleHAiOjE2MDM3ODk1OTZ9.v377ejEaI0oq3KLkT0c8Z3TfF_eTe9LP41RqTcoWyU_fnw2LMhg2ykb3JgoQzJ-1P-qfzHnrgNTHn2PTOs6Bpg"
    url = "http://localhost:8000/v1/transactions/"+str(id)+"?appid="+appid+"&appkey="+appkey
    r = requests.get(url)
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
        latest_txs = get_latest_txs()
    for tx in latest_txs:
        transaction_format(tx)
    return render_template('index.html',txs=latest_txs)

@app.route("/transactions")
def transactions():
    latest_txs = get_latest_txs()
    for tx in latest_txs:
        transaction_format(tx)
    return render_template('transactions.html',txs=latest_txs)

@app.route("/transactions/<int:id>")
def transaction(id):
    tx = get_transaction(id)
    raw_json = json.dumps(tx, indent=2)
    transaction_format(tx)
    tx['raw_json'] = raw_json
    return render_template('transaction_show.html',tx=tx)

@app.route("/transactions/<int:id>.json")
def transaction_json(id):
    tx = get_transaction(id)
    return jsonify(tx)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=False)