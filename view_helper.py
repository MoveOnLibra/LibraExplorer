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
    if 'fee' in tx:
        tx['sender_ab'] = get_address_abbrv_name(tx['sender'])
        tx['receiver_ab'] = get_address_abbrv_name(tx['receiver'])
        tx['code_name'] = _(tx['code_name'].replace("_", " "))
        tx['human_time'] = get_human_time(tx['time'])
        tx['time'] = get_time_str(tx['time'])
        tx['success'] = (tx['vm_status'] == 'executed')
        tx['gas'] = tx['fee']/1000000
        if not tx['money']:
            tx['money'] = 0
        return

    payload = tx["transaction"]
    if 'sender' in payload:
        tx['sender'] = payload['sender']
        tx['sender_ab'] = get_address_abbrv_name(payload['sender'])
        if 'receiver' in payload['script']:
            receiver = payload['script']['receiver']
            tx['receiver'] = receiver
            tx['receiver_ab'] = get_address_abbrv_name(receiver)
        if 'amount' in payload['script']:
            tx['money'] = payload['script']['amount'] / 1000_000
    else:
        tx['sender'] = _('None')
        tx['receiver'] = _('None')
        tx['sender_ab'] = _('None')
        tx['receiver_ab'] = _('None')
        tx['no_receiver'] = True

    tx['code_name'] = _(payload['type'])
    tx['code_name_full'] = payload['type']
    if 'timestamp_usecs' in payload:
        tx['human_time'] = get_human_time(payload['timestamp_usecs']//1000_000)
        tx['time'] = get_time_str(payload['timestamp_usecs']//1000_000)
    elif 'expiration_time' in payload:
        tx['human_time'] = get_human_time(payload['expiration_time'])
        tx['time'] = get_time_str(payload['expiration_time'])
    else:
        tx['human_time'] = _('None')
        tx['time'] = _('None')
    tx['success'] = (tx['vm_status'] == 'executed')

    tx['fee'] = tx['gas_used']/1000_000

    if not "money" in tx:
        tx['money'] = 0

    if len(tx['events']) == 0:
        tx['events_emit'] = 'No Events'
    else:
        tx['events_emit'] = f"{len(tx['events'])} Events"



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


