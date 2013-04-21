""" ixle.agents.typer
"""
import re
from mimetypes import guess_type

from report import report

from .base import ItemIterator

r_text = [re.compile(_) for _ in
          ['.* text']]
r_video = [re.compile(_) for _ in
           ['AVI',
            'video: .*']]
r_audio = [re.compile(_) for _ in
           ['Audio file.*',
            'MPEG ADTS']]
r_image = [re.compile(_) for _ in
           ['JPEG .*',
            'PNG .*']]

def _generic(item, r_list):
    # NOTE: assumes file_magic already ready
    if item.file_magic:
        for x in item.file_magic:
            for y in r_list:
                if y.match(x):
                    return True
    # else: use mimetype

def is_text(item): return _generic(item, r_text)
def is_video(item): return _generic(item, r_video)
def is_audio(item): return _generic(item, r_audio)
def is_image(item): return _generic(item, r_image)

MIME_MAP = dict(aa='audio', view='data', srt='text')
# used for determining file type
FEXT_MAP = dict(aa='audible-audio',
                view='couchdb-data',
                srt='subtitles',
                idx='subtitles',
                db='database-unknown')

class Mimer(ItemIterator):
    nickname = 'mimer'
    covers_fields = ['mime_type']

    def set_mime(self, item):
        typ, encoding = guess_type(item.id)
        if typ:
            report('set_mime: '+typ)
        else:
            typ = MIME_MAP.get(item.fext, None)
            report('set_consult: ' + str(typ))
        item.mime_type = typ
        self.save(item)

    def callback(self, item=None, **kargs):
        if not self.is_subagent:
            report(item.fname)
        if any([self.force, not item.mime_type]):
            self.set_mime(item)

class Typer(ItemIterator):
    nickname = 'typer'
    covers_fields = ['file_type']
    def __init__(self, *args, **kargs):
        super(Typer,self).__init__(*args, **kargs)
        self.mimer = self.subagent(Mimer)
        from ixle.agents.filer import Filer
        self.filer = self.subagent(Filer)

    def callback(self, item=None, **kargs):
        changed = False
        report(item)
        self.mimer.callback(item=item, **kargs)

        if any([self.force, not item.file_type]):
            typ = None
            changed = True
            if not item.file_magic:
                self.filer.callback(item=item)

            if is_text(item): typ = 'text'
            elif is_video(item): typ = 'video'
            elif is_audio(item): typ = 'audio'
            elif is_image(item): typ = 'image'

            more_specific = FEXT_MAP.get(item.fext, None)
            typ = more_specific or typ
            if typ is None:
                advice = item.mime_type
                if advice and 'video' in advice:
                    typ = 'video'
                else:
                    changed = False
                    print '-'*80,'\n'+'unknown file-type:', item.id
                    print item.mime_type, '::', item.file_magic
                    print '-'*80
                    return

            item.file_type = typ
            print typ, item.id
            if changed:
                self.save(item)
        else:
            print item.id, item.file_type
