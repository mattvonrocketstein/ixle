""" ixle.agents.typer
"""
from mimetypes import guess_type

from report import report
from ixle.util import report_if_verbose
from ixle.agents.base import ItemIterator
from ixle.heuristics import (FEXT_MAP, guess_mime, is_video,
                             is_crypto, is_text, is_audio, is_image)


class Mimer(ItemIterator):
    nickname = 'mimer'
    covers_fields = ['mime_type']

    def set_mime(self, item):
        typ, encoding = guess_type(item.path)
        if typ:
            report_if_verbose('set_mime: '+typ)
        else:
            typ = guess_mime(item)
            report_if_verbose('set_consult: ' + str(typ))
        item.mime_type = typ
        self.report_status('{0} for {1}'.format(typ, item.path))
        self.save(item)

    def callback(self, item=None, **kargs):
        if not self.is_subagent:
            self.report_status(item.fname)
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
        report_if_verbose(item.fname)
        self.mimer.callback(item=item, **kargs)

        if any([self.force, not item.file_type]):
            typ = None
            changed = True
            if not item.file_magic:
                self.filer.callback(item=item)

            if is_text(item):     typ = 'text'
            elif is_crypto(item): typ = 'crypto'
            elif is_video(item):  typ = 'video'
            elif is_audio(item):  typ = 'audio'
            elif is_image(item):  typ = 'image'

            more_specific = FEXT_MAP.get(item.fext, None)
            typ = more_specific or typ
            if typ is None:
                advice = item.mime_type or ''
                if item.file_magic and item.file_magic[0]=='empty':
                    typ = 'empty'
                elif 'video' in advice: typ = 'video'
                elif 'image' in advice: typ = 'image'
                else:
                    changed = False
                    #print '-'*80,'\n'+'unknown file-type:', item.path
                    #print item.mime_type, '::', item.file_magic
                    #print '-'*80
                    return

            item.file_type = typ
            #print typ, item.path
            if changed:
                self.save(item)
        else:
            report_if_verbose(item.path, item.file_type)
