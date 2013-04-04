




from Page import Page
from bitcoinrpc.authproxy import JSONRPCException
from utilities import format_bytes
from pprint import pprint
from StringIO import StringIO

from utilities import btc_to_satoshi, calculate_tx_fee_satoshi,\
    format_satoshi, format_bytes, format_time, \
    calculate_tx_input_satoshi, calculate_tx_output_satoshi,\
    htmlize_tx_info, htmlize_blk_info
    



class RawTransactionView(Page):
    def service(self,request, response):
        
        response.setContentType('text/plain')
        writer = response.getWriter()
        access = self.server.create_access()
        config = self.server.config
        
        option_tx_get_txs = True
        
        txid = request.getParameter("txid")
        
        
        if txid is None:
            
            
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
            
            
            pprint(tx_info,writer)
            
            
        except JSONRPCException as e:
            
            
            writer = response.getWriter()
            writer.pln('Error: {error}'.format(error=str(e.error)))
            #raise

