
from decimal import Decimal

from time import gmtime, strftime,time

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

