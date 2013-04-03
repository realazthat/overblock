
class Page:
    
    def __init__(self,basehandler):
        self.basehandler = basehandler
        self.server = basehandler.server
    def service(self,request, response):
        raise NotImplementedError()

