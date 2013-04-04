

from Page import Page
from bitcoinrpc.authproxy import JSONRPCException
from utilities import format_bytes,calc_reward_satoshi,btc_to_satoshi,\
    format_relative_time, format_satoshi, format_time,\
    htmlize_blk_info
from pprint import pprint

from time import gmtime, strftime,time

class BlockView(Page):
    def service(self,request, response):
        
        print 'BlockView'
        try:
            access = self.server.create_access()
            config = self.server.config
            
            def configure_options():
                option_blk_get_txs = request.getParameter('blk_get_txs')
                option_blk_get_tx_inputs = request.getParameter('blk_get_tx_inputs')
                
                if option_blk_get_txs != None:
                    if option_blk_get_txs == '1':
                        option_blk_get_txs = True
                    elif option_blk_get_txs == '0':
                        option_blk_get_txs = False
                    else:
                        option_blk_get_txs = None
                if option_blk_get_tx_inputs != None:
                    if option_blk_get_tx_inputs == '1':
                        option_blk_get_tx_inputs = True
                    elif option_blk_get_tx_inputs == '0':
                        option_blk_get_tx_inputs = False
                    else:
                        option_blk_get_tx_inputs = None
                    
                
                
                if option_blk_get_txs is None:
                    option_blk_get_txs = config['blk_get_txs']
                if option_blk_get_txs is None:
                    option_blk_get_tx_inputs = config['blk_get_tx_inputs']
                return option_blk_get_txs,option_blk_get_tx_inputs
            
            option_blk_get_txs,option_blk_get_tx_inputs = configure_options()
            
            
            option_blk_get_tx_inputs = option_blk_get_txs and option_blk_get_tx_inputs
            
            
            rawtransactions = {}
            
            blk_hash = request.getParameter('hash')
            
            if blk_hash is None:
                height = request.getParameter('height')
                
                if height is None:
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
            
            
            def write_top_header_bar():
                writer.pln('<div class="top-header-bar">')
                
                
                writer.pln('<strong>Nav:</strong> <a href="/">Main Page</a>')
                
                
                writer.pln('<!-- end of top-header-bar -->')
                writer.pln('</div>')
            write_top_header_bar()
            
            def write_top_title_bar():
                writer.pln('<div class="top-title-bar">')
                
                
                writer.pln('<h2>Block</h2> <h4>View information about a bitcoin block.</h4>')
                
                
                writer.pln('<span class="top-title-bar-button-field">')
                """
                url_parts = urlparse.urlparse(path)
                query = urlparse.parse_qs(url_parts.query, True)
                """
                
                
                fastest_detail_text = 'Fastest detail{default_comment}'.format(default_comment= (' (default)' if not config['blk_get_txs'] else '') )
                some_detail_text = 'Some detail{default_comment}'.format(default_comment= (' (default)' if config['blk_get_txs'] and not config['blk_get_tx_inputs'] else '') )
                most_detail_text = 'Most detail{default_comment}'.format(default_comment= (' (default)' if config['blk_get_tx_inputs'] else '') )
                
                if not option_blk_get_txs:
                    writer.pln(fastest_detail_text)
                else:
                    writer.pln('<a href="/block?hash={hash}&blk_get_txs=0">{text}</a>'.format(hash=blk_hash,text=fastest_detail_text))
                
                writer.pln(' | ')
                
                if option_blk_get_txs and not option_blk_get_tx_inputs:
                    writer.pln(some_detail_text)
                else:
                    writer.pln('<a href="/block?hash={hash}&blk_get_txs=1">{text}</a>'.format(hash=blk_hash,text=some_detail_text))
                
                writer.pln(' | ')
                
                if option_blk_get_txs and option_blk_get_tx_inputs:
                    writer.pln(most_detail_text)
                else:
                    writer.pln('<a href="/block?hash={hash}&blk_get_txs=1&blk_get_tx_inputs=1">{text}</a>'.format(hash=blk_hash,text=most_detail_text))
                
                
                writer.pln('</span>')
                
                
                writer.pln('<!-- end of top-header-bar -->')
                writer.pln('</div>')
            write_top_title_bar()
            
            writer.pln('<table class="block-hashes-table">')
            writer.pln('<tr><th colspan="2">Hashes</th></tr>')
            
            
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
            writer.pln('<th colspan="2">Summary</th>')
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
                writer.pln('<td>N/A (requires options <i>blk_get_txs</i> and <i>blk_get_tx_inputs</i>)</td>')
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
                
                if tx_fee_satoshi is None or not(tx_fee_satoshi>0):
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
            
            
            htmlize_blk_info(writer,blk_info)
            
            writer.pln('</body></html>')
        except JSONRPCException as e:
            
            raise
        
        
