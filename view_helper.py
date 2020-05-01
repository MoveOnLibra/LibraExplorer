import libra
from canoser import hex_to_int_list
from libra.bytecode import bytecodes
from datetime import datetime, timezone
from flask_babel import _
import pdb

def event_format(ev, account_field):
    ev['account'] = ev['event_data_decode'][account_field]
    ev['account_ab'] = get_address_abbrv_name(ev['account'])
    money = ev['event_data_decode']['amount']
    ev['money'] = money / 1000000

def account_format(account):
    if "decoded_account_resource" in account:
        account['authentication_key'] = account['decoded_account_resource']['authentication_key']
        account['balance'] = account['balance']/1000000
        account['sequence_number'] = account['decoded_account_resource']['sequence_number']
    else:
        account['authentication_key'] = ''
        account['balance'] = 0
        account['sequence_number'] = 0


def transaction_format(tx):
    if 'sender' in tx:
        tx['sender_ab'] = get_address_abbrv_name(tx['sender'])
        tx['receiver_ab'] = get_address_abbrv_name(tx['receiver'])
        tx['code_name'] = _(tx['code_name'])
        tx['human_time'] = get_human_time(tx['time'])
        tx['time'] = get_time_str(tx['time'])
        tx['success'] = (tx['major_status'] == 4001)
        return
    if 'proposer' in tx:
        sender = tx['proposer']
        tx['sender'] = sender
        tx['sender_ab'] = get_address_abbrv_name(sender)
        tx['money'] = "0"
        tx['no_receiver'] = True
        tx['human_time'] = get_human_time(tx['timestamp_usecs'] // 1000_000)
        tx['time'] = get_time_str(tx['timestamp_usecs'] // 1000_000)
        tx['code_name'] = _('BlockMetadata')
        tx['success'] = (tx['transaction_info']['major_status'] == 4001)
        tx['events_emit'] = 'No Events'
        return
    if 'write_set' in tx:
        sender = libra.AccountConfig.core_code_address()
        tx['sender'] = sender
        tx['sender_ab'] = get_address_abbrv_name(sender)
        if 'version' not in tx:
            tx['version'] = 0
        tx['money'] = "0"
        tx['no_receiver'] = True
        tx['human_time'] = ''
        tx['time'] = ''
        tx['code_name'] = _('Genesis')
        tx['success'] = True
        tx['events_emit'] = f"{len(tx['events'])} Events"
        return
    payload = tx['raw_txn']['payload']
    sender = tx['raw_txn']['sender']
    tx['sender'] = sender
    tx['sender_ab'] = get_address_abbrv_name(sender)
    if tx['sender_ab'] == "Libra Association":
        tx['sender_text_class'] = 'text-info'
    else:
        tx['sender_text_class'] = 'text-primary'
    try:
        receiver = payload['Script']['args'][0]['Address']
        money = payload['Script']['args'][1]['U64']/1000000
        tx['money'] = money
        tx['receiver'] = receiver
        tx['receiver_ab'] = get_address_abbrv_name(receiver)
        if tx['receiver_ab'] == "Libra Association":
            tx['receiver_text_class'] = 'text-info'
        else:
            tx['receiver_text_class'] = 'text-primary'
    except Exception:
        tx['money'] = "0"
        tx['no_receiver'] = True
    tx['human_time'] = get_human_time(tx['raw_txn']['expiration_time'])
    tx['time'] = get_time_str(tx['raw_txn']['expiration_time'])
    tx['code_name'] = get_tx_abbreviation_name(payload, tx['version'])
    tx['success'] = (tx['transaction_info']['major_status'] == 4001)
    try:
        if len(tx['events']) == 0:
            tx['events_emit'] = 'No Events'
        else:
            tx['events_emit'] = f"{len(tx['events'])} Events"
    except KeyError:
        pass


def get_tx_abbreviation_name(payload, version):
    if version == 0:
        return _("Genesis")
    if list(payload)[0] != "Script":
        return list(payload)[0]
    code = hex_to_int_list(payload['Script']['code'])
    if code == bytecodes["mint"]:
        return _("mint")
    if code == bytecodes["peer_to_peer"]:
        return _("p2p")
    if code == bytecodes["peer_to_peer_with_metadata"]:
        return _("p2p_m")
    if code == bytecodes["create_account"]:
        return _("new account")
    if code == bytecodes["rotate_authentication_key"]:
        return _("rotate key")
    return _("script")

def get_address_abbrv_name(address):
    if address == libra.account_config.AccountConfig.association_address():
        return _("Libra Association")
    else:
        return address

def get_human_time(unix_timestamp):
    if unix_timestamp > 2**63:
        return _("N/A")
    diff = datetime.now().timestamp() - unix_timestamp
    if diff >= 0:
        suffix = _("ago")
    else:
        suffix = _("later")
    diff = int(abs(diff)) // 60
    if diff == 0:
        return _("just now")
    if diff < 60:
        return f"{diff}" + _(' mins ') + f"{suffix}"
    if diff < 60*24:
        return f"{diff//60}" + _(' hours ') + f"{diff%60}" + _(' mins ') + f"{suffix}"
    diff = diff // 60
    return f"{diff // 24}" + _(' day ') + f"{diff % 24}" + _(' hours ') + f"{suffix}"

def get_time_str(unix_timestamp):
    if unix_timestamp > 2**63:
        return _("N/A")
    utc_time = datetime.fromtimestamp(unix_timestamp, timezone.utc)
    local_time = utc_time.astimezone()
    return local_time.strftime("%Y-%m-%d %H:%M:%S%z")


def format_metadata(meta):
    meta['start_time_str'] = get_time_str(meta['start_time'])
    meta['latest_time_str'] = get_time_str(meta['latest_time'])
    meta['total_transactions_format'] = f"{meta['total_transactions']:,}"
    meta['total_user_transactions_format'] = f"{meta['total_user_transactions']:,}"


