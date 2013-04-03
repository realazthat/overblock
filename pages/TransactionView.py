




from Page import Page
from bitcoinrpc.authproxy import JSONRPCException
from utilities import format_bytes
from pprint import pprint
from StringIO import StringIO

from utilities import btc_to_satoshi, calculate_tx_fee_satoshi,\
    format_satoshi, format_bytes, format_time, \
    calculate_tx_input_satoshi, calculate_tx_output_satoshi,\
    htmlize_tx_info, htmlize_blk_info
    



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
        
            src_tx_infos = {}
            if option_tx_get_txs:
                for tx_input in tx_info['vin']:
                    if 'txid' in tx_input:
                        src_txid = tx_input['txid']
                        src_tx_info = access.getrawtransaction(src_txid,1)
                        rawtransactions[src_txid] = src_tx_info
                        
                        src_tx_infos[src_txid] = src_tx_info
        
        
        
            writer.pln('<html><head><link rel="stylesheet" href="/style.css"></head><body>')
            
            coinbase = False
            
            for tx_input in tx_info['vin']:
                if 'coinbase' in tx_input:
                    coinbase = True
            
            
            
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
                
                
                
                
                assert option_tx_get_txs
                tx_fee_satoshi = calculate_tx_fee_satoshi(tx_info,src_tx_infos)
                
                
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
                            
                            if option_tx_get_txs:
                                
                                src_tx_info = src_tx_infos[src_txid]
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
            
            write_transaction_info()
            
            
            
            
            
            
            
            
            
            writer.pln('<table class="transaction-summary-table">')
            
            
            writer.pln('<tr>')
            writer.pln('<th colspan="2">Summary</th>')
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
                
            else:
                writer.pln('<tr>')
                writer.pln('<td>Included in block</td>')
                writer.pln('<td><a href="/block?height={height}">{height}</a></td>'.format(height=height))
                writer.pln('</tr>')
                
                writer.pln('<tr>')
                writer.pln('<td>Confirmations</td>')
                writer.pln('<td>{confirmations} Confirmations</td>'.format(confirmations=tx_info['confirmations']))
                writer.pln('</tr>')
            
        
            writer.pln('</table>')
            
            
            if not coinbase:
                writer.pln('<table class="transaction-input-output-table">')
                writer.pln('<tr>')
                writer.pln('<th colspan="2">Inputs and Outputs</th>')
                writer.pln('</tr>')
                
                
                if option_tx_get_txs:
                    total_input_satoshi = calculate_tx_input_satoshi(tx_info, src_tx_infos)
                    
                    writer.pln('<tr>')
                    writer.pln('<td>Total Input</td>')
                    writer.pln('<td>{total_input}</td>'.format(total_input=format_satoshi(total_input_satoshi)))
                    writer.pln('</tr>')
                
                
                total_output_satoshi = calculate_tx_output_satoshi(tx_info)
                
                writer.pln('<tr>')
                writer.pln('<td>Total Output</td>')
                writer.pln('<td>{total_output}</td>'.format(total_output=format_satoshi(total_output_satoshi)))
                writer.pln('</tr>')
                
                if option_tx_get_txs:
                    total_fee_satoshi = calculate_tx_fee_satoshi(tx_info, src_tx_infos)
                    
                    writer.pln('<tr>')
                    writer.pln('<td>Fees</td>')
                    writer.pln('<td>{fee}</td>'.format(fee=format_satoshi(total_fee_satoshi)))
                    writer.pln('</tr>')
                    
                
                writer.pln('</table>')
            
            
            htmlize_tx_info(writer,tx_info)
            
            htmlize_blk_info(writer,blk_info)
            
            writer.pln('</body></html>')
            
        except JSONRPCException as e:
            
            raise

