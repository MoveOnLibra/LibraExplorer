import os
import requests, json
import pytest
import pdb

import app


def test_mol_api():
    host = "http://apitest.MoveOnLibra.com"
    url = "/v1/transactions/latest?limit=20"
    with pytest.raises(Exception) as excinfo:
        response = requests.get(host+url, timeout=0.001)
    error = excinfo.value
    assert type(error) == requests.exceptions.ConnectTimeout


