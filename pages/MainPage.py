

from time import gmtime, strftime,time
from Page import Page
from bitcoinrpc.authproxy import JSONRPCException
from utilities import format_bytes,calc_reward_satoshi,btc_to_satoshi,\
    format_relative_time,format_satoshi,format_bytes_places
from pprint import pprint

class MainPage(Page):
    
    def service(self,request, response):
        print 'MainPage'
        
        
        access = self.server.create_access()
        config = self.server.config
        
        option_blk_get_txs = config['blk_get_txs']
        
        blockcount = access.getblockcount()
        
        #print 'blockcount:',blockcount
        
        k = config['k_most_recent']
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



        
        
