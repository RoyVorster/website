import mongoengine as me
from datetime import datetime

from jinja2 import Template

import re

NOTE_COLORS = ['rgba(141, 163, 201, 0.3)', 'rgba(0, 128, 0, 0.3)', 'rgba(204, 139, 139, 0.3)']

class Note(me.Document):
    content = me.StringField(required=True)
    index = me.IntField(required=True)
    ts = me.DateTimeField(required=True)

    meta = {
        'ordering': ['-index']
    }

class Note_out:
    def __init__(self, note_doc):
        self.content = note_doc.content
        self.index = note_doc.index

        self.ts = note_doc.ts
        self.date, self.time = '', ''

        self.color = ''

        # Init
        self.set_date_time()
        self.set_color()

    def set_color(self):
        self.color = NOTE_COLORS[int(self.ts.strftime("%d")) % 3]

    def set_date_time(self):
        self.date = self.ts.strftime("%Y-%m-%d")
        self.time = self.ts.strftime("%H:%M:%S")

# Quick wrapper
def create_note(content, ts):
    prev = Note.objects.first()
    if prev is not None:
        if content == prev.content or len(content) == 0:
            return

        index = prev.index + 1
    else:
        index = 0

    content = content.replace('\n', '<br>')

    n = Note(content=content, index=index, ts=ts)
    n.save()

def delete_note(idx):
    Note.objects(index=idx).first().delete()

def get_notes():
    yield from map(Note_out, Note.objects)


# Main io functions
def render(template):
    return Template(template.render(notes=list(get_notes())))

def handle_request(request):
    if 'note_submit' in request.keys():
        # If textarea is empty
        if 'note_input' in request.keys():
            content, ts = request['note_input'][0], datetime.now()
            create_note(content, ts)

    if 'note_delete' in request.keys():
        idx = request['note_delete'][0]
        idx = int(re.sub("[^0-9]", "", idx))

        delete_note(idx)