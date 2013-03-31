







from servlet_original import HttpServer,HttpServlet
import bitcoinrpc

import urlparse
from time import gmtime, strftime,time
from bitcoinrpc.authproxy import AuthServiceProxy,JSONRPCException
from pprint import pprint
from decimal import Decimal
            

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
        
    
    
class DemuxServlet(HttpServlet):
    def __init__(self,request, client_address, server):
        self.init_params = {'request':request,'client_address':client_address,'server':server}
        HttpServlet.__init__(self,request,client_address,server)
        
        
        #print 'request:',request
        
        
    def service(self,request, response):
        #sever.path
        #print 'path:',self.path
        
        path = urlparse.urlparse(self.path).path
        
        
                
        if path not in self.server.paths:
        
            self.send_error(404)
            return
        
        
        cls = self.server.paths[path]
        
        path_servlet = cls(self)

        path_servlet.service(request,response)


class Page:
    
    def __init__(self,basehandler):
        self.basehandler = basehandler
        self.server = basehandler.server
    def service(self,request, response):
        raise NotImplementedError()

class MainPage(Page):
    
    def service(self,request, response):
        print 'MainPage'
        
        
        access = self.server.create_access()
        config = self.server.config
        
        option_blk_get_txs = config['blk_get_txs']
        
        blockcount = access.getblockcount()
        
        #print 'blockcount:',blockcount
        
        k = 10
        last_k_block_hashes = {}
        blks_info = {}
        blks_total_sent = {}
                
        for blk_index in range(blockcount-k-1,blockcount):
            blk_hash = access.getblockhash(blk_index)
            last_k_block_hashes[blk_index] = blk_hash
            
            blk_info = access.getblock(blk_hash)
            blks_info[blk_hash] = blk_info
            
            

        response.setContentType('text/html')
        
        writer = response.getWriter()

        
        writer.pln('<html><head><link rel="stylesheet" href="/style.css"></head><body>')
        
        
        writer.pln('<div class="most-recent-blocks-section">')
        
        writer.pln('<h3>Most Recent Blocks</h3>')
        writer.pln('<table class="most-recent-blocks-table">')
        writer.pln('<tr><th>Height</th><th>Age</th><th>Transactions</th><th>Total Sent</th><th>Size</th></tr>')
        
        current_time = time()
        
        for blk_index in reversed(range(blockcount-k-1,blockcount)):
            blk_hash = last_k_block_hashes[blk_index]
            blk_info = blks_info[blk_hash]
            
            
            total_sent_satoshi = None
            
            if option_blk_get_txs:
                total_sent_satoshi = 0
                
                for txid in blk_info['tx']:
                    tx_info = access.getrawtransaction(txid,1)
                
                    for tx_output in tx_info['vout']:
                        
                        total_sent_satoshi += btc_to_satoshi(tx_output['value'])
            
            
            
            
            writer.pln('<tr>')
            writer.pln('<td><a href="/block?height={height}">{height}</a></td>'.format(height=blk_info['height']))
            
            
            writer.pln('<td>{age}</td>'.format(age=format_relative_time(current_time - blk_info['time'])))
            writer.pln('<td>{transactions}</td>'.format(transactions=len(blk_info['tx'])))
            
            if option_blk_get_txs:
                writer.pln('<td>{total_sent}</td>'.format(total_sent=format_satoshi(total_sent_satoshi)))
            else:
                writer.pln('<td>N/A (settings)</td>')
            writer.pln('<td>{size}</td>'.format(size=format_bytes_places(blk_info['size'],2)))            
            
            writer.pln('</tr>')
            
        
        writer.pln('</table>')
        
        writer.pln('<!-- end of most-recent-blocks-section -->')
        writer.pln('</div>')

        writer.pln('</body></html>')


class BlockView(Page):
    def service(self,request, response):
        
        print 'BlockView'
        try:
            access = self.server.create_access()
            config = self.server.config
            option_blk_get_tx_inputs = config['blk_get_tx_inputs']
            option_blk_get_txs = config['blk_get_txs']
            
            rawtransactions = {}
            
            blk_hash = request.getParameter('hash')
            
            if blk_hash == None:
                height = request.getParameter('height')
                
                if height == None:
                    response.setContentType('text/html')
                    
                    writer = response.getWriter()
                    writer.pln('Invalid block identifier')
                    self.basehandler.send_error(404)
                    return
                    
                height = int(height)
                
                
                blockcount = access.getblockcount()
                
                
                if not (height < blockcount):
                    response.setContentType('text/html')
                    
                    writer = response.getWriter()
                    writer.pln('Invalid block; not yet in blockchain. blockcount: {blockcount}'.format(blockcount=blockcount))
                    self.basehandler.send_error(404)
                    return
                
                blk_hash = access.getblockhash(height)
                
                
                
            
            blk_info = access.getblock(blk_hash)
            
            height = blk_info['height']
            reward_satoshi = calc_reward_satoshi(height)
            
            response.setContentType('text/html')
            
            
            tx_infos = {}
            
            if option_blk_get_txs:
                for txid in blk_info['tx']:
                    tx_info = access.getrawtransaction(txid,1)
                    tx_infos[txid] = tx_info
                    rawtransactions[txid] = tx_info
            
        
                if option_blk_get_tx_inputs:
                    
                    for txid,tx_info in tx_infos.iteritems():
                        tx_input_value = 0
                        for txin in tx_info['vin']:
                            
                            if 'txid' in txin:
                                in_txid = txin['txid']
                                in_tx_outidx = txin['vout']
                                in_tx_info = access.getrawtransaction(in_txid,1)
                                
                                rawtransactions[in_txid] = in_tx_info
                                
            
            def calculate_tx_input_satoshi(txid):
                if not option_blk_get_txs:
                    return None
                if not option_blk_get_tx_inputs:
                    return None
                
                tx_info = tx_infos[txid]
                tx_total_input_value_satoshi = 0
                for src_tx_entry in tx_info['vin']:
                    
                    if 'txid' in src_tx_entry:
                        src_txid = src_tx_entry['txid']
                        src_tx_outidx = src_tx_entry['vout']
                        src_tx_info = rawtransactions[src_txid]
                        
                        tx_total_input_value_satoshi += btc_to_satoshi(src_tx_info['vout'][src_tx_outidx]['value'])
                return tx_total_input_value_satoshi
            def calculate_tx_output_satoshi(txid):
                if not option_blk_get_txs:
                    return None
                    

                
                tx_info = tx_infos[txid]
                
                
                tx_total_output_value = 0
                for tx_output in tx_info['vout']:
                    tx_total_output_value += btc_to_satoshi(tx_output['value'])
                
                return tx_total_output_value
                
            def is_tx_coinbase(txid):
                tx_info = tx_infos[txid]
                
                for tx_input in tx_info['vin']:
                    if 'coinbase' in tx_input:
                        return True
                return False
                    
                
            def calculate_tx_fee_satoshi(txid):
                if not option_blk_get_txs:
                    return None
                if not option_blk_get_tx_inputs:
                    return None
                
                if is_tx_coinbase(txid):
                    return 0
                
                tx_total_output_value = calculate_tx_output_satoshi(txid)
                tx_total_input_value = calculate_tx_input_satoshi(txid)
                
                tx_fee_satoshi = tx_total_input_value - tx_total_output_value
                
                assert tx_fee_satoshi >= 0
                
                return tx_fee_satoshi
            
            
            writer = response.getWriter()
            
            
            
            writer.pln('<html><head><link rel="stylesheet" href="/style.css"></head><body>')
            
            writer.pln('<table class="block-hashes-table">')
            writer.pln('<th><td colspan="2"><h3>Hashes</th></tr>')
            
            
            writer.pln('<tr>')
            writer.pln('<td>Hash</td>')
            writer.pln('<td><a href="/block?hash={hash}">{hash}</a>'.format(hash=blk_info['hash']))
            writer.pln('</tr>')
            
            writer.pln('<tr>')
            writer.pln('<td>Previous Block</td>')
            writer.pln('<td><a href="/block?hash={previousblockhash}">{previousblockhash}</a></td>'.format(previousblockhash=blk_info['previousblockhash']))
            writer.pln('</tr>')
            
            if 'nextblockhash' in blk_info:
                writer.pln('<tr>')
                writer.pln('<td>Next Block</td>')
                writer.pln('<td><a href="/block?hash={nextblockhash}">{nextblockhash}</a></td>'.format(nextblockhash=blk_info['nextblockhash']))
                writer.pln('</tr>')
            
            
            writer.pln('<tr>')
            writer.pln('<td>Merkle Root</td>')
            writer.pln('<td>{merkleroot}</td>'.format(merkleroot=blk_info['merkleroot']))
            writer.pln('</tr>')
            
            
            writer.pln('</table>')
            
            
            
            
            writer.pln('<table class="block-summary-table">')
            
            
            writer.pln('<tr>')
            writer.pln('<td colspan="2"><h3>Summary</h3></td>')
            writer.pln('</tr>')
            
            writer.pln('<tr>')
            writer.pln('<td>Number of Transactions</td>')
            writer.pln('<td>{transactions}</td>'.format(transactions=len(blk_info['tx'])))
            writer.pln('</tr>')
            
            
            if option_blk_get_txs:
                output_total_satoshi = 0
                for txid in blk_info['tx']:
                    tx_info = tx_infos[txid]
                    
                    for txout in tx_info['vout']:
                        output_total_satoshi += btc_to_satoshi(txout['value'])
                        
                
                writer.pln('<tr>')
                writer.pln('<td>Output Total</td>')
                writer.pln('<td>{output_total}</td>'.format(output_total=format_satoshi(output_total_satoshi)))
                writer.pln('</tr>')
            else:
                
                writer.pln('<tr>')
                writer.pln('<td>Output Total</td>')
                writer.pln('<td>N/A (turn on <i>blk_get_txs</i> in settings)</td>')
                writer.pln('</tr>')
            
            if option_blk_get_txs and option_blk_get_tx_inputs:
                total_fees_satoshi = 0
                
                for txid in blk_info['tx']:
                    tx_fee_satoshi = calculate_tx_fee_satoshi(txid)
                    if tx_fee_satoshi != None:
                        total_fees_satoshi += tx_fee_satoshi
                
                
                writer.pln('<tr>')
                writer.pln('<td>Transaction Fees</td>')
                writer.pln('<td>{tx_fees}</td>'.format(tx_fees=format_satoshi(total_fees_satoshi)))
                writer.pln('</tr>')
            else:
                
                writer.pln('<tr>')
                writer.pln('<td>Transaction Fees</td>')
                writer.pln('<td>N/A (requires options <i>blk_get_txs</i> and <i>blk_get_tx_inputs</i></td>')
                writer.pln('</tr>')
            
            
            writer.pln('<tr>')
            writer.pln('<td>Height</td>')
            writer.pln('<td><a href="/block?height={height}">{height}</a></td>'.format(height=height))
            writer.pln('</tr>')
            
            writer.pln('<tr>')
            writer.pln('<td>Timestamp</td>')
            writer.pln('<td>{timestamp}</td>'.format(timestamp=format_time(blk_info['time'])))
            writer.pln('</tr>')
            
            writer.pln('<tr>')
            writer.pln('<td>Difficulty</td>')
            writer.pln('<td>{difficulty}</td>'.format(difficulty=blk_info['difficulty']))
            writer.pln('</tr>')
            
            
            writer.pln('<tr>')
            writer.pln('<td>Bits</td>')
            writer.pln('<td>{bits}</td>'.format(bits=int(blk_info['bits'],16)))
            writer.pln('</tr>')
            
            
            writer.pln('<tr>')
            writer.pln('<td>Size</td>')
            writer.pln('<td>{size}</td>'.format(size=format_bytes(blk_info['size'])))
            writer.pln('</tr>')
            
            writer.pln('<tr>')
            writer.pln('<td>Version</td>')
            writer.pln('<td>{version}</td>'.format(version=blk_info['version']))
            writer.pln('</tr>')
            
            writer.pln('<tr>')
            writer.pln('<td>Nonce</td>')
            writer.pln('<td>{nonce}</td>'.format(nonce=blk_info['nonce']))
            writer.pln('</tr>')
            
            writer.pln('<tr>')
            writer.pln('<td>Block Reward</td>')
            writer.pln('<td>{reward}</td>'.format(reward=format_satoshi(reward_satoshi)))
            writer.pln('</tr>')
            
            
            
            
            
            writer.pln('</table>')
            
            
            
            
            
            writer.pln('<div class="transactions-section">')
            writer.pln('<h3>Transactions</h3> Transactions contained within this block.')
            
            
            for txid in blk_info['tx']:
                
                if not option_blk_get_txs:
                    
                    writer.pln('<div class="transaction-section">')
                    writer.pln('<a href="#txid_{txid}"/>'.format(txid=txid))
                    
                    writer.pln('<div class="transaction-section-header">')
                    writer.pln('<span style=""><a href="/transaction?txid={txid}">{txid}</a></span>'.format(txid=txid))
                    writer.pln('</div>')
                    
                    
                    
                    writer.pln('</div>')
                    
                    continue
                
                tx_info = tx_infos[txid]
                
                tx_total_output_value_satoshi = 0
                for txout in tx_info['vout']:
                    if 'value' in txout:
                        tx_total_output_value_satoshi += btc_to_satoshi(txout['value'])
                
                
                
                
                
                tx_fee_satoshi = calculate_tx_fee_satoshi(txid)
                
                
                writer.pln('<div class="transaction-section">')
                
                
                writer.pln('<div class="transaction-section-header">')
                writer.pln('<span style=""><a href="/transaction?txid={txid}">{txid}</a></span>'.format(txid=txid))
                
                if tx_fee_satoshi == None or not(tx_fee_satoshi>0):
                    writer.pln('<span style="float:right"><strong>(Size: {size}) {time}</strong></span>'.format(size=format_bytes(len(tx_info['hex'])/2), time=format_time(tx_info['time'])))
                    
                else:
                    writer.pln('<span style="float:right"><strong>(Fee: {fee} - Size: {size}) {time}</strong></span>'.format(fee=format_satoshi(tx_fee_satoshi),
                                                                                                                             size=format_bytes(len(tx_info['hex'])/2),
                                                                                                                             time=format_time(tx_info['time'])))
                writer.pln('</div>')
                
                
                def write_inputs():
                    writer.pln('<div class="tx-inputs">')
                    writer.pln('<h4>Inputs</h4>')
                    
                    src_txids = []
                    for src_tx in tx_info['vin']:
                        
                        if 'txid' in src_tx:
                            src_txid,src_out_index = src_tx['txid'],src_tx['vout']
                            src_txids.append((src_txid,src_out_index))
                    
                    if len(src_txids) > 0:
                        
                        writer.pln('<table class="tx-inputs-table">')
                        
                        
                        for src_txid,src_out_index in src_txids:
                            
                            writer.pln('<tr>')
                            writer.pln('<td><a href="/transaction?txid={src_txid}">{src_txid}</a>[<a href="/transaction?txid={src_txid}&output_idx={src_out_index}#output_{src_out_index}">{src_out_index}</a>]</td>'.format(src_txid=src_txid,src_out_index=src_out_index))
                            
                            if option_blk_get_tx_inputs:
                                
                                src_tx_info = rawtransactions[src_txid]
                                src_output_value_satoshi = btc_to_satoshi(src_tx_info['vout'][src_out_index]['value'])
                                writer.pln('<td>{src_output_value}</td>'.format(src_output_value=format_satoshi(src_output_value_satoshi)))
                        
                            writer.pln('</tr>')
                        writer.pln('</table>')
                    else:
                        writer.pln('<strong>No Inputs (Newly Generated Coins)</strong>')
                
                    writer.pln('</div>')
                write_inputs()
                
                def write_outputs():
                    writer.pln('<div class="tx-outputs">')
                    writer.pln('<h4>Outputs</h4>')
                    
                    writer.pln('<table class="tx-outputs-table">')
                    
                    for txout in tx_info['vout']:
                        writer.pln('<tr>')
                        
                        addresses = []
                        
                        
                        if 'scriptPubKey' in txout:
                            if 'addresses' in txout['scriptPubKey']:
                                for address in txout['scriptPubKey']['addresses']:
                                    addresses.append(address)
                        
                        
                        writer.pln('<td>')
                        if len(addresses) > 0:
                            writer.pln('<ul>')
                            
                            for address in addresses:
                                
                                writer.pln('<li>{address}</li>'.format(address=address))
                            writer.pln('</ul>')
                        writer.pln('</td>')
                        writer.pln('<td>{value}</td>'.format(value=format_satoshi(btc_to_satoshi(txout['value']))))
                        
                            
                        writer.pln('</tr>')
                        
                        
                        
                    writer.pln('</table>')

                    
                    writer.pln('</div>')
                
                write_outputs()
                
                
                
                
                
                
                
                writer.pln('<div class="transaction-section-footer">')
                writer.pln('<div class="transaction-total-output">{transaction_total_output}</div>'.format(transaction_total_output=format_satoshi(tx_total_output_value_satoshi)))
                writer.pln('</div>')
                
                #writer.pln('<pre>')
                
                #pprint(tx_info,writer)
                
                #writer.pln('</pre>')
                
                
                writer.pln('<!-- end transaction-section -->')
                writer.pln('</div>')
            
            writer.pln('<!-- end transactions-section -->')
            writer.pln('</div>')
            writer.pln('<div class="clear"/>')
            
            
            writer.pln('<pre>')
            
            pprint(blk_info,writer)
            
            writer.pln('</pre>')
            
            writer.pln('</body></html>')
        except JSONRPCException as e:
            
            raise
        
        

class TransactionView(Page):
    def service(self,request, response):
        
        response.setContentType('text/html')
        writer = response.getWriter()
        access = self.server.create_access()
        config = self.server.config
        
        option_tx_get_txs = True
        
        txid = request.getParameter("txid")
        
        
        if txid == None:
            
            
            writer = response.getWriter()
            writer.pln('Invalid txid')
            self.basehandler.send_error(404)
            return
        
        try:
            
            
            rawtransactions = {}
            
            tx_info = access.getrawtransaction(txid,1)
            rawtransactions[txid] = tx_info
            
            blk_hash = tx_info['blockhash']
            
            blk_info = access.getblock(blk_hash)
            height = blk_info['height']
        
        
            writer.pln('<html><head><link rel="stylesheet" href="/style.css"></head><body>')
            
            coinbase = False
            
            for tx_input in tx_info['vin']:
                if 'coinbase' in tx_input:
                    coinbase = True
            
            
            
            """
            def write_transaction_info():
                
                if not option_tx_get_txs:
                    
                    writer.pln('<div class="transaction-section">')
                    writer.pln('<a href="#txid_{txid}"/>'.format(txid=txid))
                    
                    writer.pln('<div class="transaction-section-header">')
                    writer.pln('<span style=""><a href="/transaction?txid={txid}">{txid}</a></span>'.format(txid=txid))
                    writer.pln('</div>')
                    
                    
                    
                    writer.pln('</div>')
                    
                    return
                
                tx_total_output_value_satoshi = 0
                for txout in tx_info['vout']:
                    if 'value' in txout:
                        tx_total_output_value_satoshi += btc_to_satoshi(txout['value'])
                
                
                
                
                
                tx_fee_satoshi = calculate_tx_fee_satoshi(txid)
                
                
                writer.pln('<div class="transaction-section">')
                
                
                writer.pln('<div class="transaction-section-header">')
                writer.pln('<span style=""><a href="/transaction?txid={txid}">{txid}</a></span>'.format(txid=txid))
                
                if tx_fee_satoshi == None or not(tx_fee_satoshi>0):
                    writer.pln('<span style="float:right"><strong>(Size: {size}) {time}</strong></span>'.format(size=format_bytes(len(tx_info['hex'])/2), time=format_time(tx_info['time'])))
                    
                else:
                    writer.pln('<span style="float:right"><strong>(Fee: {fee} - Size: {size}) {time}</strong></span>'.format(fee=format_satoshi(tx_fee_satoshi),
                                                                                                                             size=format_bytes(len(tx_info['hex'])/2),
                                                                                                                             time=format_time(tx_info['time'])))
                writer.pln('</div>')
                
                
                def write_inputs():
                    writer.pln('<div class="tx-inputs">')
                    writer.pln('<h4>Inputs</h4>')
                    
                    src_txids = []
                    for src_tx in tx_info['vin']:
                        
                        if 'txid' in src_tx:
                            src_txid,src_out_index = src_tx['txid'],src_tx['vout']
                            src_txids.append((src_txid,src_out_index))
                    
                    if len(src_txids) > 0:
                        
                        writer.pln('<table class="tx-inputs-table">')
                        
                        
                        for src_txid,src_out_index in src_txids:
                            
                            writer.pln('<tr>')
                            writer.pln('<td><a href="/transaction?txid={src_txid}">{src_txid}</a>[<a href="/transaction?txid={src_txid}&output_idx={src_out_index}#output_{src_out_index}">{src_out_index}</a>]</td>'.format(src_txid=src_txid,src_out_index=src_out_index))
                            
                            if option_blk_get_tx_inputs:
                                
                                src_tx_info = rawtransactions[src_txid]
                                src_output_value_satoshi = btc_to_satoshi(src_tx_info['vout'][src_out_index]['value'])
                                writer.pln('<td>{src_output_value}</td>'.format(src_output_value=format_satoshi(src_output_value_satoshi)))
                        
                            writer.pln('</tr>')
                        writer.pln('</table>')
                    else:
                        writer.pln('<strong>No Inputs (Newly Generated Coins)</strong>')
                
                    writer.pln('</div>')
                write_inputs()
                
                def write_outputs():
                    writer.pln('<div class="tx-outputs">')
                    writer.pln('<h4>Outputs</h4>')
                    
                    writer.pln('<table class="tx-outputs-table">')
                    
                    for txout in tx_info['vout']:
                        writer.pln('<tr>')
                        
                        addresses = []
                        
                        
                        if 'scriptPubKey' in txout:
                            if 'addresses' in txout['scriptPubKey']:
                                for address in txout['scriptPubKey']['addresses']:
                                    addresses.append(address)
                        
                        
                        writer.pln('<td>')
                        if len(addresses) > 0:
                            writer.pln('<ul>')
                            
                            for address in addresses:
                                
                                writer.pln('<li>{address}</li>'.format(address=address))
                            writer.pln('</ul>')
                        writer.pln('</td>')
                        writer.pln('<td>{value}</td>'.format(value=format_satoshi(btc_to_satoshi(txout['value']))))
                        
                            
                        writer.pln('</tr>')
                        
                        
                        
                    writer.pln('</table>')

                    
                    writer.pln('</div>')
                
                write_outputs()
                
                
                
                
                
                
                
                writer.pln('<div class="transaction-section-footer">')
                writer.pln('<div class="transaction-total-output">{transaction_total_output}</div>'.format(transaction_total_output=format_satoshi(tx_total_output_value_satoshi)))
                writer.pln('</div>')
                
                
                writer.pln('<!-- end transaction-section -->')
                writer.pln('</div>')
            
            
            """
            
            
            
            
            
            
            
            
            writer.pln('<table class="block-summary-table">')
            
            
            writer.pln('<tr>')
            writer.pln('<th colspan="2"><h3>Summary</h3></th>')
            writer.pln('</tr>')
            
            writer.pln('<tr>')
            writer.pln('<td>Size</td>')
            writer.pln('<td>{size}</td>'.format(size=format_bytes(len(tx_info['hex'])/2)))
            writer.pln('</tr>')
            
            if coinbase:
                
                writer.pln('<tr>')
                writer.pln('<td>Reward From Block</td>')
                writer.pln('<td><a href="/block?height={height}">{height}</a></td>'.format(height=height))
                writer.pln('</tr>')
                
            
            writer.pln('</table>')
            
            writer.pln('<pre>')
            
            pprint(tx_info,writer)
            
            writer.pln('</pre>')
            writer.pln('<pre>')
            
            pprint(blk_info,writer)
            
            writer.pln('</pre>')
            
            writer.pln('</body></html>')
            
        except JSONRPCException as e:
            
            raise
        
        
        

class StyleSheet(Page):
    
    def service(self,request, response):
        with open('style.css','r') as f:
            
            css = f.read()
            response.setContentType('text/css')
            
            writer = response.getWriter()
            
            writer.write(css)
        
        
        

def main():
    
    import yaml

    config_file = open('config.yml')

    config = None

    try:
        config = yaml.load(config_file)
    except:
        print
        print "ERROR: parsing configuration"
        print
        
        raise


    def create_access():
        return AuthServiceProxy(config['rpcserverurl'])

     
    
    

    HttpServer.allow_reuse_address = True
    DemuxServlet.debug(True)

    port = 51234
    httpd = HttpServer(('', port), DemuxServlet)
    httpd.__debug = True
    
    httpd.paths = { '/': MainPage, '/block': BlockView, '/transaction': TransactionView, '/style.css': StyleSheet}
    httpd.create_access = create_access
    httpd.config = config
    
    try:
        while True:
            httpd.handle_request()
    finally:
        httpd.socket.close()
        pass
    
    pass


if __name__ == "__main__":
    main()
