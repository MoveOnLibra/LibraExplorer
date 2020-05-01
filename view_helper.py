import libra
from canoser import hex_to_int_list
from libra.transaction_scripts import bytecodes
from libra.bytecode import get_script_name
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
        tx['code_name'] = _(tx['code_name'].replace("_", " "))
        tx['human_time'] = get_human_time(tx['time'])
        tx['time'] = get_time_str(tx['time'])
        tx['success'] = (tx['major_status'] == 4001)
        tx['gas'] = tx['fee']/1000000
        if not tx['money']:
            tx['money'] = 0
        return
    if 'proposer' in tx:
        sender = tx['proposer']
        tx['sender'] = sender
        tx['sender_ab'] = get_address_abbrv_name(sender)
        tx['money'] = "0"
        tx['no_receiver'] = True
        tx['human_time'] = get_human_time(tx['timestamp_usecs'] // 1000_000)
        tx['time'] = get_time_str(tx['timestamp_usecs'] // 1000_000)
        tx['code_name'] = _('block meta')
        tx['code_name_full'] = _('BlockMetadata')
        tx['success'] = (tx['transaction_info']['major_status'] == 4001)
        tx['events_emit'] = 'No Events'
        tx['gas'] = tx['transaction_info']['gas_used']/1000000
        return
    if 'write_set' in tx:
        sender = libra.AccountConfig.core_code_address()
        tx['sender'] = sender
        tx['sender_ab'] = get_address_abbrv_name(sender)
        if 'version' not in tx:
            tx['version'] = 0
        tx['money'] = "0"
        tx['no_receiver'] = True
        tx['human_time'] = _('None')
        tx['time'] = _('None')
        tx['code_name'] = _('Genesis')
        tx['code_name_full'] = _('Genesis')
        tx['success'] = True
        tx['events_emit'] = f"{len(tx['events'])} Events"
        tx['gas'] = 0
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
    tx['code_name_full'] = get_tx_full_name(payload, tx['version'])
    tx['success'] = (tx['transaction_info']['major_status'] == 4001)
    tx['gas'] = tx['transaction_info']['gas_used']/1000000
    try:
        if len(tx['events']) == 0:
            tx['events_emit'] = 'No Events'
        else:
            tx['events_emit'] = f"{len(tx['events'])} Events"
    except KeyError:
        pass


def get_tx_abbreviation_name(payload, version):
    return get_tx_full_name(payload, version)


def get_tx_full_name(payload, version):
    if version == 0:
        return _("Genesis")
    if list(payload)[0] != "Script":
        return list(payload)[0]
    code = bytes.fromhex(payload['Script']['code'])
    return _(get_script_name(code))


def get_address_abbrv_name(address):
    if address == libra.account_config.AccountConfig.association_address():
        return _("Libra Association")
    elif address is None:
        return _("None")
    else:
        return address[0:8] + "..." + address[-7:-1]

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


