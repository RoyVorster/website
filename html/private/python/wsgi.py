import os.path, sys
sys.path.insert(0, os.path.dirname(__file__))

from mongoengine import connect
from jinja2 import Template
from urllib.parse import parse_qs

# Local modules
from modules import notes

connect('website')

class application:
    def __init__(self, environ, start_response):
        self.environ, self.start_response = environ, start_response

    def __iter__(self):
        # Check for POST
        try:
            request_size = int(self.environ.get('CONTENT_LENGTH', 0))

            if request_size > 0:
                request_body = str(self.environ['wsgi.input'].read(request_size))

                # Handle
                inputs(request_body)
        except ValueError:
            request_size = 0

        # Response
        self.start_response(self.get_status(), self.get_response_header())

        # Render page
        html = render()
        yield str.encode(html)

    def get_status(self):
        return '200 OK'

    def get_response_header(self):
        return [('Content-type','text/html')]


# Main input handler
def inputs(request):
    request = parse_qs(request)
    request = {k.strip("b'"): v for k, v in request.items()}

    print(str(request)) # Print to apache log

    # Notes
    notes.handle_request(request)

# Main render function
def render():
    with open(get_file_name('index.j2.html')) as f:
        page = Template(f.read())

    # Notes
    page = notes.render(page)

    return page.render()

# Quick utils
def get_file_name(f_name):
    root = os.path.realpath(os.path.dirname(__file__))
    return os.path.join(root, f_name)