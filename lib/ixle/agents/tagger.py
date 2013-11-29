""" ixle.agents.tagger
"""

import mutagen
from report import report
from ixle.schema import Item
from .base import ItemIterator

from hachoir_metadata import metadata
from collections import defaultdict
from pprint import pprint

from hachoir_metadata import metadata
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
def clean_tags(tags):
    """ the asf stuff below may apply to 'wma' files """
    for k,v in tags.items():
        if type(v) in [mutagen.asf.ASFDWordAttribute]:
            tags[k] = int(v)
        if type(v) in [mutagen.asf.ASFGUIDAttribute,
                       mutagen.asf.ASFByteArrayAttribute,
                       mutagen.asf.ASFQWordAttribute,
                       ]:
            tags.pop(k)
        if type(v) in [mutagen.asf.ASFUnicodeAttribute]:
            tags[k] = unicode(v)
    return tags

def hachm(filename):
    # using this example http://archive.org/details/WorkToFishtestwmv
    try:
        filename, realname = unicodeFilename(filename), filename
    except TypeError:
        filename,realname=filename,filename
    parser = createParser(filename)
    # See what keys you can extract
    tmp = metadata.extractMetadata(parser)
    if tmp is None: return {}
    else: tmp = tmp._Metadata__data.iteritems()
    for k,v in tmp:
        if v.values:
            print v.key, v.values[0].value
    # Turn the tags into a defaultdict
    metalist = metadata.extractMetadata(parser).exportPlaintext()
    meta = defaultdict(defaultdict)

    for item in metalist[1:]:
        item = [x.strip() for x in item.split('-') if x.strip()][0]
        item = [ x.strip().lower().replace(' ','_') for x in item.split(':') ]

        k,v = item.pop(0),':'.join(item)
        meta[k]=v
    return meta

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

    def tagger_callback(self,item=None,**kargs):
        m = hachm(item.path)
        if m:
            m=dict(m)
        else: m={}
        item.tags = m
        self.save(item)

class MusicTagger(GenericTagger):
    nickname = 'mtagger'

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
