







from servlet import HttpServer,HttpServlet
import bitcoinrpc

import urlparse
from bitcoinrpc.authproxy import AuthServiceProxy,JSONRPCException
from pprint import pprint
from decimal import Decimal

from pages.RawBlockView import RawBlockView
from pages.RawTransactionView import RawTransactionView
from pages.TransactionView import TransactionView
from pages.BlockView import BlockView
from pages.MainPage import MainPage
from pages.Page import Page

    
    
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

    port = config['listen_port']
    httpd = HttpServer(('', port), DemuxServlet)
    httpd.__debug = True
    
    httpd.paths = { '/': MainPage, '/block': BlockView, '/transaction': TransactionView, '/style.css': StyleSheet, '/rawtransaction': RawTransactionView, '/rawblock': RawBlockView}
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
