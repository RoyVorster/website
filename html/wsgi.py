'''
Main page with form and button
    POST: Store text in some folder -> later: markdown

    Get all files in that folder and output. Jinja templating engine
'''

from jinja2 import Template
from datetime import datetime
import re
import os.path

NOTE_FOLDER = 'notes'

class application:
    def __init__(self, environ, start_response):
        self.environ, self.start_response = environ, start_response

    def __iter__(self):
        try:
            request_size = int(self.environ.get('CONTENT_LENGTH', 0))

            if request_size > 0:
                request_body = str(self.environ['wsgi.input'].read(request_size))
                text = request_body.split('=')[-1][:-1]
                text = text.replace('+', ' ')

                if len(text) > 0:
                    add_note(text)

        except ValueError:
            request_size = 0

        self.start_response(self.get_status(), self.get_response_header())

        html = render()
        yield str.encode(html)

    def get_status(self):
        return '200 OK'

    def get_response_header(self):
        return [('Content-type','text/html')]

# Render
class Note:
    def __init__(self, text, date, time):
        self.text = text

        self.date = date
        self.time = time

def render():
    d_name = get_file_name(NOTE_FOLDER)
    ns = parse_notes(d_name)

    with open(get_file_name('index.html.j2')) as f:
        page = Template(f.read())

    return page.render(notes=ns)

def parse_notes(d_name):
    def parse(f_name):
        with open(f_name) as f:
            dat = [l.strip('\n') for l in f.readlines()]

        return Note(text=''.join(dat[2:]), date=dat[0], time=dat[1])

    # Filter files and sort
    d = filter(lambda f: os.path.isfile(os.path.join(d_name, f)), os.listdir(d_name))
    d = reversed(sorted(list(d), key=lambda f: int(os.path.splitext(f)[0])))

    d = map(lambda f: os.path.join(d_name, f), d)
    return list(map(parse, d))

# Add note
def add_note(text):
    now = datetime.now()
    d, t = now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

    f_name = re.sub('[^0-9]', '', ''.join([d, t]))
    with open(get_file_name(os.path.join(NOTE_FOLDER, f_name)), 'w') as f_out:
        f_out.write('\n'.join([d, t, text]))

# Quick utils
def get_file_name(f_name):
    root = os.path.realpath(os.path.dirname(__file__))
    return os.path.join(root, f_name)