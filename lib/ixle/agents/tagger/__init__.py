""" ixle.agents.tagger
"""

import mutagen
from report import report
from ixle.schema import Item
from ixle.agents.base import ItemIterator

from .util import hachm, clean_tags

class GenericTagger(ItemIterator):
    covers_fields = ['tags']
    DEBUG = True

    def callback(self, item=None, **kargs):
        from ixle.exceptions import FileDoesntExist
        if not item.exists():
            err = 'item does not exist: ' + item.fname
            self.report_error(err)
            return dict(error=FileDoesntExist(err))
        return self.tagger_callback(item=item, **kargs)

class ImageTagger(GenericTagger):
    nickname = 'itagger'
    covers_fields = [] # only generictagger should do this..
    def tagger_callback(self,item=None,**kargs):
        m = hachm(item.path)
        if m:
            m=dict(m)
        else: m={}
        item.tags = m
        self.save(item)

class MusicTagger(GenericTagger):
    nickname = 'mtagger'
    covers_fields = [] # only generictagger should do this..
    def _query_override(self):
        if not self.path:
            return Item.objects.filter(fext__in=['mp3'])

    def tagger_callback(self, item=None, **kargs):
        if any([self.force, not item.tags]):
            report(item.fname)
            from mutagen.flac import FLACNoHeaderError
            from mutagen.mp3 import HeaderNotFoundError
            try:
                f = mutagen.File(item.path, easy=True)
            except (EOFError, FLACNoHeaderError,
                    HeaderNotFoundError), e:
                self.report_error("error decoding: "+str(e))
                return
            if f is not None:
                data = f.info.__dict__.copy() # bitrate, etc
                try:
                    data.update(f)
                except mutagen.easyid3.EasyID3KeyError:
                    self.report_error('error in __getitem__ for EasyID3')
                    return
                for k, v in data.items():
                    if isinstance(v, list):
                        if len(v)==1:
                            item.tags[k] = v[0]
                            continue
                        elif len(v)==0:
                            continue
                    item.tags[k] = v
                else:
                    self.report_status("got tags, but they were empty.")
                if item.tags:
                    item.tags=clean_tags(item.tags)
                    self.save(item)
            else:
                self.report_status(
                    "file exists but cannot open"
                    " mutagen File object.. is this a music file?")
