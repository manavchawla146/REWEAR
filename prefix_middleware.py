class PrefixMiddleware:
    """
    WSGI middleware to handle subdirectory hosting.
    This middleware strips the prefix from the request path before passing to Flask
    and ensures Flask generates URLs with the correct prefix.
    """
    
    def __init__(self, app, prefix='/rewear'):
        self.app = app
        self.prefix = prefix
        
    def __call__(self, environ, start_response):
        # If the request path starts with our prefix, strip it
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            if not environ['PATH_INFO']:
                environ['PATH_INFO'] = '/'
            environ['SCRIPT_NAME'] = self.prefix
        
        # Handle static files specifically
        if environ['PATH_INFO'].startswith('/static/'):
            environ['SCRIPT_NAME'] = self.prefix
            
        return self.app(environ, start_response)
