'''
Main page with form and button
    POST: Store text in some folder -> later: markdown

    Get all files in that folder and output. Jinja templating engine
'''

from jinja2 import Template

class Application:
    def __init__(self, environ, start_response):
        self.environ, self.start_response = environ, start_response

    def __iter__(self):
        self.start_response(get_status(), get_response_header())


        html = self.render()
        yield str.encode(html)

    def render(self):
        with open('index.html.j2') as f:
            page = Template(f.read())

        page.render(some_text='lol')

        return page

    def get_status():
        return '200 OK'

    def get_response_header():
        return [('Content-type','text/html')]
