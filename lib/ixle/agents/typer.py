""" ixle.agents.typer
"""
import re
from mimetypes import guess_type
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
           ['JPEG .*']]

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

class Typer(ItemIterator):

    def set_mime(self, item):
        typ, encoding = guess_type(item.id)
        if typ:
            print 'set_mime: ', typ, item.id
        else:
            MIME_MAP = dict(srt='text')
            typ = MIME_MAP.get(item.fext, None)
            print 'set_consult: ', typ, item.id
        item.mime_type = typ
        self.save(item)

    def callback(self, item=None, **kargs):
        changed = False
        if any([self.force,not item.mime_type]):
            self.set_mime(item)

        if any([self.force, not item.file_type]):
            typ = None
            changed = True
            if is_text(item):
                FEXT_MAP = dict(srt='subtitles')
                more_specific = FEXT_MAP.get(item.fext,None)
                if more_specific:
                    typ = more_specific
                else:
                    typ = 'text'
            elif is_video(item): typ = 'video'
            elif is_audio(item): typ = 'audio'
            elif is_image(item): typ = 'image'
            else:
                changed = False
                print '-'*80
                print 'unknown file-type:', item.id
                print item.file_magic
                print '-'*80
                return

            item.file_type = typ
            print typ, item.id
            if changed:
                self.save(item)
        else:
            print item.id, item.file_type
