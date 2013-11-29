""" ixle.agents.tagger.util
"""
import mutagen
from report import report
from ixle.schema import Item
from ixle.agents.base import ItemIterator

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
