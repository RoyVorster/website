# Main wsgi application

def application(environ,start_response):
    status, response_header = '200 OK', [('Content-type','text/html')]
    start_response(status,response_header)

    return [b"LOL"]