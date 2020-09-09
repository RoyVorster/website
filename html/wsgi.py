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

        html = render()
        yield str.encode(html)

    def get_status(self):
        return '200 OK'

    def get_response_header(self):
        return [('Content-type','text/html')]


# Render
class Note:
    def __init__(self, text, date):
        self.text = text
        self.date = date

def render():
    d_name = get_file_name('articles')
    ns = parse_notes(d_name)

    with open(get_file_name('index.html.j2')) as f:
        page = Template(f.read())

    return page.render(notes=ns)

def parse_notes(d_name):
    def parse(f_name):
        with open(f_name) as f:
            dat = [l.strip('\n') for l in f.readlines()]

        return Note(text=''.join(dat[1:]), date=dat[0])

    d = filter(lambda f: os.path.isfile(os.path.join(d_name, f)), os.listdir(d_name))

    d = map(lambda f: os.path.join(d_name, f), d)
    return list(map(parse, d))


# Quick utils
def get_file_name(f_name):
    root = os.path.realpath(os.path.dirname(__file__))
    return os.path.join(root, f_name)