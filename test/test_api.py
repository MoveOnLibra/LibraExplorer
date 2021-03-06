import os
import requests, json
import pytest
import pdb

import app


def test_mol_api():
    host = "http://apitest.MoveOnLibra.com"
    url = "/v1/libra/about"
    params = {}
    headers = app.gen_api_header(False, "explorer.moveonlibra.com")
    assert len(headers.items()) == 1
    response = requests.get(host+url, params=params, headers=headers)
    assert response.status_code == 200
    assert response.headers["API-Server"] == "MoveOnLibra-API"
    assert response.headers['Access-Control-Allow-Origin'] == "*"
    assert response.headers["Libra-network"] == "testnet"
    assert int(response.headers["Latest-Version"]) >= 0
    data = json.loads(response.content.decode('utf-8-sig'))
    assert data['network_name'] == "Libra TESTNET"
    assert data["url"] == "https://client.testnet.libra.org"
    assert data["core_code_address"] == "0"*31 + "1"
    assert data["start_time"] <= data["latest_time"]
    assert data["total_transactions"] >= 1


def test_mol_api_proxy():
    host = "http://apitest.MoveOnLibra.com"
    url = "/v1/libra/about"
    params = {}
    headers = app.gen_api_header(False, "47.254.29.109-33333.explorer.moveonlibra.com")
    assert headers["RealSwarm"] == "47.254.29.109-33333"
    response = requests.get(host+url, params=params, headers=headers)
    return # devnet currently down.
    assert response.status_code == 200
    assert response.headers["API-Server"] == "MoveOnLibra-API"
    assert response.headers['Access-Control-Allow-Origin'] == "*"
    assert response.headers["Libra-Network"] == "47.254.29.109-33333"
    assert int(response.headers["Latest-Version"]) >= 0
    data = json.loads(response.content.decode('utf-8-sig'))
    assert data['network_name'] == "Anonymous network"
    assert data["url"] == "http://47.254.29.109:33333"
    assert data["start_time"] <= data["latest_time"]
    assert data["total_transactions"] >= 1
