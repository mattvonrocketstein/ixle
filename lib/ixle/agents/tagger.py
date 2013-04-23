""" ixle.agents.tagger
"""

import mutagen
from report import report

from ixle.query import javascript
from .base import ItemIterator

class Tagger(ItemIterator):
    nickname = 'tagger'
    covers_fields = ['tags']

    def _query_override(self):
        if not self.path:
            return javascript.find_equal(fieldname='fext',
                                         value='mp3')

    def callback(self, item=None, **kargs):
        if any([self.force, not item.tags]):
            report(item.fname)
            try:
                f = mutagen.File(item.abspath, easy=True)
            except (EOFError, mutagen.flac.FLACNoHeaderError,
                    mutagen.mp3.HeaderNotFoundError), e:
                report("error decoding: "+str(e))
                return
            if f is not None:
                data = f.info.__dict__.copy() # bitrate, etc
                try:
                    data.update(f)
                except mutagen.easyid3.EasyID3KeyError:
                    report('error in __getitem__ for EasyID3')
                    return
                for k, v in data.items():
                    if isinstance(v, list):
                        if len(v)==1:
                            item.tags[k] = v[0]
                            continue
                        elif len(v)==0:
                            continue
                    item.tags[k] = v
                if item.tags:
                    self.save(item)
