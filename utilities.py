
from decimal import Decimal

from time import gmtime, strftime,time
from copy import deepcopy
from pprint import pprint


def calc_reward_satoshi(height):
    return 5000000000 / 2**(int(height / 210000))

def format_btc(btc):
    if btc == 0:
        return '0 BTC'
    
    btc = Decimal(btc)
    
    def remove_exponent(d):
        '''Remove exponent and trailing zeros.

        >>> remove_exponent(Decimal('5E+3'))
        Decimal('5000')

        '''
        return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()
    
    val = str(btc)
    
    if val.find('.') != -1:
        val = val.rstrip('0')
        if val[-1] == '.':
            val += '0'
    
    return val + " BTC"

def btc_to_satoshi(btc):
    
    value = Decimal(btc) * 10**8
    
    new_value = int(value)
    assert value == new_value
    
    return new_value
    
    

def format_satoshi(satoshi):
    
    return format_btc(Decimal(satoshi) / 10**8)


def format_bytes_places(n,places):
    PLACES = Decimal(10)**-places
    
    if n < (1 << 10):
        return str(Decimal(n).quantize(PLACES)) + " bytes"
    elif n < (1 << 20):
        return '{KiB} KiB'.format(KiB=(Decimal(n) / (1 << 10)).quantize(PLACES))
    elif n < (1 << 30):
        return '{MiB} MiB'.format(MiB=(Decimal(n) / (1 << 20)).quantize(PLACES))
    else:
        return '{GiB} GiB'.format(GiB=(Decimal(n) / (1 << 30)).quantize(PLACES))

def format_bytes(n):
    if n < (1 << 10):
        return str(Decimal(n)) + " bytes"
    elif n < (1 << 20):
        return '{KiB} KiB'.format(KiB=(Decimal(n) / (1 << 10)))
    elif n < (1 << 30):
        return '{MiB} MiB'.format(MiB=(Decimal(n) / (1 << 20)))
    else:
        return '{GiB} GiB'.format(GiB=(Decimal(n) / (1 << 30)))

def format_time(t):
    return strftime('%Y-%m-%d %H:%M:%S',gmtime(t))

def format_relative_time(t):
    
    minute_seconds = 60
    hour_seconds = minute_seconds * 60
    day_seconds = hour_seconds * 24
    year_seconds = day_seconds * 365
    
    if t < minute_seconds:
        return '{seconds} seconds'.format(seconds=t)
    elif t < hour_seconds:
        return '{minutes} minutes'.format(minutes=int(t/minute_seconds))
    elif t < day_seconds:
        hours = int(t/hour_seconds)
        minutes = int((t - (hours*hour_seconds)) / minute_seconds)
        return '{hours} hours {minutes} minutes'.format(hours=hours,minutes=minutes)
    #elif t < year_seconds:
    
    days = int(t/day_seconds)
    hours = int((t - (days*day_seconds)) / hour_seconds)
    return '{hours} hours {minutes} minutes'.format(hours=hours,minutes=minutes)


def calculate_tx_input_satoshi(tx_info,src_tx_infos):
    
    """
    if not option_blk_get_txs:
        return None
    if not option_blk_get_tx_inputs:
        return None
    """
    
    #tx_info = tx_infos[txid]
    tx_total_input_value_satoshi = 0
    for src_tx_entry in tx_info['vin']:
        
        if 'txid' in src_tx_entry:
            src_txid = src_tx_entry['txid']
            src_tx_outidx = src_tx_entry['vout']
            assert src_txid in src_tx_infos and "LOGIC ERROR, THE NECESSARY INPUT TXs WERE NOT COLLECTED FOR THIS CALL DUE TO SETTINGS, PLEASE CHECK SETTING BEFORE MAKING CALL"
            src_tx_info = src_tx_infos[src_txid]
            
            tx_total_input_value_satoshi += btc_to_satoshi(src_tx_info['vout'][src_tx_outidx]['value'])
    return tx_total_input_value_satoshi

def calculate_tx_output_satoshi(tx_info):


    tx_total_output_value = 0
    for tx_output in tx_info['vout']:
        tx_total_output_value += btc_to_satoshi(tx_output['value'])

    return tx_total_output_value

def is_tx_coinbase(tx_info):
    
    for tx_input in tx_info['vin']:
        if 'coinbase' in tx_input:
            return True
    return False

def calculate_tx_fee_satoshi(tx_info,src_tx_infos):
    
    if is_tx_coinbase(tx_info):
        return 0
    
    tx_total_output_value = calculate_tx_output_satoshi(tx_info)
    tx_total_input_value = calculate_tx_input_satoshi(tx_info,src_tx_infos)
    
    tx_fee_satoshi = tx_total_input_value - tx_total_output_value
    
    assert tx_fee_satoshi >= 0
    
    return tx_fee_satoshi



def htmlize_tx_info(writer,tx_info):
    tx_info = deepcopy(tx_info)
    
    
    
    blockhash = tx_info['blockhash']
    txid = tx_info['txid']
    tx_info['blockhash'] = '<a href="/block?hash={blockhash}">{blockhash}</a>'.format(blockhash=blockhash)
    tx_info['txid'] = '<a href="/transaction?txid={txid}">{txid}</a>'.format(txid=txid)
    
    for src_tx_input_entry in tx_info['vin']:
        if 'txid' in src_tx_input_entry:
            src_txid = src_tx_input_entry['txid']
            src_tx_input_entry['txid'] = '<a href="/transaction?txid={src_txid}">{src_txid}</a>'.format(src_txid=src_txid)
        
        
            src_txid_output_index = src_tx_input_entry['vout']
            src_tx_input_entry['vout'] = '<a href="/transaction?txid={src_txid}&output_index={vout}#output_{vout}">{vout}</a>'.format(src_txid=src_txid,vout=src_txid_output_index)
    
    for output_entry in tx_info['vout']:
        output_entry['value'] = format_satoshi(btc_to_satoshi(output_entry['value']))
    
    writer.pln('<pre>')
    
    pprint(tx_info,writer)
    
    writer.pln('</pre>')



def htmlize_blk_info(writer,blk_info):
    blk_info = deepcopy(blk_info)
    
    blockhash = blk_info['hash']
    height = blk_info['height']
    difficulty = blk_info['difficulty']
    blk_info['hash'] = '<a href="/block?hash={blockhash}">{blockhash}</a>'.format(blockhash=blockhash)
    blk_info['height'] = '<a href="/block?height={height}">{height}</a>'.format(height=height)
    blk_info['difficulty'] = '{difficulty}'.format(difficulty=difficulty)
    
    if 'previousblockhash' in blk_info:
        blk_info['previousblockhash'] = '<a href="/block?hash={previousblockhash}">{previousblockhash}</a>'.format(previousblockhash=blk_info['previousblockhash'])
    if 'nextblockhash' in blk_info:
        blk_info['nextblockhash'] = '<a href="/block?hash={nextblockhash}">{nextblockhash}</a>'.format(nextblockhash=blk_info['nextblockhash'])
    
    txids = blk_info['tx']
    
    for i in xrange(len(txids)):
        txid = txids[i]
        txids[i] = '<a href="/transaction?txid={txid}">{txid}</a>'.format(txid=txid)
        
    writer.pln('<pre>')
    
    pprint(blk_info,writer)
    
    writer.pln('</pre>')


def ascii_ize(value):
    
    if isinstance(value,unicode):
        return value.encode('ascii')
    
    
    if isinstance(value,list):
        result = []
        for element in value:
            result.append(ascii_ize(element))
        return result
    
    if isinstance(value,dict):
        
        result = {}
        for key,item in value.iteritems():
            akey = ascii_ize(key)
            aitem = ascii_ize(item)
            result[akey] = aitem
        return result
    
    return value



