'''
Main page with form and button
    POST: Store text in some folder -> later: markdown

    Get all files in that folder and output. Jinja templating engine
'''

from jinja2 import Template
import os.path

class application:
    def __init__(self, environ, start_response):
        self.environ, self.start_response = environ, start_response

    def __iter__(self):
        self.start_response(self.get_status(), self.get_response_header())

        html = self.render()
        yield str.encode(html)

    def render(self):
        with open(get_file('index.html.j2')) as f:
            page = Template(f.read())

        return page.render(some_text='lol')

    def get_status(self):
        return '200 OK'

    def get_response_header(self):
        return [('Content-type','text/html')]

def get_file(f_name):
    root = os.path.realpath(os.path.dirname(__file__))
    return os.path.join(root, f_name)