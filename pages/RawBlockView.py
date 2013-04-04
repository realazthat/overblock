

from Page import Page
from bitcoinrpc.authproxy import JSONRPCException
from utilities import format_bytes,calc_reward_satoshi,btc_to_satoshi,\
    format_relative_time, format_satoshi, format_time,\
    htmlize_blk_info
from pprint import pprint
from copy import deepcopy
from time import gmtime, strftime,time

class RawBlockView(Page):
    def service(self,request, response):
        
        print 'BlockView'
        try:
            access = self.server.create_access()
            config = self.server.config
            
            rawtransactions = {}
            
            blk_hash = request.getParameter('hash')
            
            if blk_hash is None:
                height = request.getParameter('height')
                
                if height is None:
                    response.setContentType('text/plain')
                    
                    writer = response.getWriter()
                    writer.pln('Invalid block identifier')
                    self.basehandler.send_error(404)
                    return
                    
                height = int(height)
                
                
                blockcount = access.getblockcount()
                
                
                if not (height < blockcount):
                    response.setContentType('text/plain')
                    
                    writer = response.getWriter()
                    writer.pln('Invalid block; not yet in blockchain. blockcount: {blockcount}'.format(blockcount=blockcount))
                    self.basehandler.send_error(404)
                    return
                
                blk_hash = access.getblockhash(height)
            
            
            
            response.setContentType('text/plain')
            
            
            blk_info = access.getblock(blk_hash)
            
            
            blk_info_ascii = {}
            
            
            for key,item in blk_info.iteritems():
                value = deepcopy(item)
                
                
                
                if isinstance(value,unicode):
                    value = value.encode('ascii')
                
                blk_info_ascii[key.encode('ascii')] = value
            
            
            transaction_entries = blk_info_ascii['tx']
            
            for i in xrange(len(transaction_entries)):
                transaction_entries[i] = transaction_entries[i].encode('ascii')
                
            
            writer = response.getWriter()
            pprint(blk_info_ascii,writer)
        except JSONRPCException as e:
            
            raise
        
        
