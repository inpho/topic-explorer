from bottle import install, redirect, request, ServerAdapter

def redirect_http_to_https(callback):
    '''Bottle plugin that redirects all http requests to https'''

    def wrapper(*args, **kwargs):
        scheme = request.urlparts[0]
        if scheme == 'http':
            # request is http; redirect to https
            redirect(request.url.replace('http', 'https', 1))
        else:
            # request is already https; okay to proceed
            return callback(*args, **kwargs)
    return wrapper

# copied from bottle. Only changes are to import ssl and wrap the socket
class SSLWSGIRefServer(ServerAdapter):
    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        import ssl
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        
        certfile = self.options.pop('certfile', 'server.pem')

        srv = make_server(self.host, self.port, handler, **self.options)
        srv.socket = ssl.wrap_socket (
            srv.socket,
            certfile=certfile,  # path to certificate
            server_side=True)
        srv.serve_forever()
