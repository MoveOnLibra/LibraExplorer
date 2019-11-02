from flask import Flask, flash, redirect, render_template, request, session, abort
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
        return _('Error: the translation service failed.')
    data = json.loads(r.content.decode('utf-8-sig'))
    return data


app = Flask(__name__)
latest_txs = None

@app.route("/")
def index():
    global latest_txs
    if latest_txs is None:
        latest_txs = get_latest_txs()
    for tx in latest_txs:
        transaction_format(tx)
    return render_template('index.html',txs=latest_txs)


if __name__ == "__main__":
    app.run()