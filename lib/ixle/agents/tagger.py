""" ixle.agents.tagger
"""

import mutagen
from report import report

from ixle.util import javascript
from ixle.heuristics import guess_mime, is_video, is_text, is_audio, is_image
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
            except (EOFError, mutagen.mp3.HeaderNotFoundError), e:
                report("error decoding")
                return
            if f is not None:
                data=f.info.__dict__.copy() # bitrate, etc
                data.update(f)
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
