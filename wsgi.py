# Main wsgi application

def application(environ,start_response):
    status = '200 OK'

    html = 'LOL'

    response_header = [('Content-type','text/html')]
    start_response(status,response_header)
    return [html]