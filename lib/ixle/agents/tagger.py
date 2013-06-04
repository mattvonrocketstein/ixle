""" ixle.agents.tagger
"""

import mutagen
from report import report

from ixle.query import javascript
from .base import ItemIterator

from hachoir_metadata import metadata
from collections import defaultdict
from pprint import pprint

from hachoir_metadata import metadata
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser

def hachm(filename):
    # using this example http://archive.org/details/WorkToFishtestwmv
    try:
        filename, realname = unicodeFilename(filename), filename
    except TypeError:
        filename,realname=filename,filename
    parser = createParser(filename)
    # See what keys you can extract
    tmp = metadata.extractMetadata(parser)._Metadata__data.iteritems()
    for k,v in tmp:
        if v.values:
            print v.key, v.values[0].value
    # Turn the tags into a defaultdict
    metalist = metadata.extractMetadata(parser).exportPlaintext()
    meta = defaultdict(defaultdict)
    #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    for item in metalist[1:]:
        item = [x.strip() for x in item.split('-') if x.strip()][0]
        item = [ x.strip().lower().replace(' ','_') for x in item.split(':') ]

        k,v = item.pop(0),':'.join(item)
        meta[k]=v
    return meta

class GenericTagger(ItemIterator):
    pass

class ImageTagger(ItemIterator):
    covers_fields = ['tags']
    DEBUG = True
    nickname = 'itagger'

    def callback(self, item=None, **kargs):
        m = hachm(item.id)
        if m:
            m=dict(m)
        else: m={}
        item.tags = m
        self.save(item)

class Tagger(ItemIterator):
    nickname = 'tagger'
    covers_fields = ['tags']
    DEBUG = True

    def _query_override(self):
        if not self.path:
            return javascript.find_equal(fieldname='fext',
                                         value='mp3')

    def callback(self, item=None, **kargs):
        if not item.exists():
            self.report_error('item does not exist: ' + item.fname)
            return
        if any([self.force, not item.tags]):
            report(item.fname)
            try:
                f = mutagen.File(item.abspath, easy=True)
            except (EOFError, mutagen.flac.FLACNoHeaderError,
                    mutagen.mp3.HeaderNotFoundError), e:
                report("error decoding: "+str(e))
                self.record['count_error']+=1
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
                else:
                    report("got tags, but they were empty.")
                if item.tags:
                    self.save(item)
            else:
                report("file exists but cannot open mutagen File object")
