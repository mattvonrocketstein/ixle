""" ixle.util.epub
"""
from ixle.python import ope
from epubzilla.epubzilla import Epub
from collections import defaultdict, namedtuple

class EpubTag(namedtuple('EpubTag','name text extra')):
    @property
    def is_isbn(self):
        return self.name=='identifier' and \
               self.extra.get('scheme','').lower()=='isbn'

def get_tags_epub(fname=None, epub=None):
    """ sample output follows:

     [[u'publisher', 'Open Road Media', {}],
      [u'meta',
       '',
       {u'content': 'Annapurna: The First Conquest of an 8,000-Meter Peak',
        u'name': 'calibre:title_sort'}],
      [u'language', 'en', {}],
      [u'creator',
       'Herzog, Maurice',
       {u'file-as': 'Herzog, Maurice', u'role': 'aut'}],
      [u'meta',
       '',
       {u'content': '2014-04-03T17:30:29.793187+00:00',
        u'name': 'calibre:timestamp'}],
      [u'title', 'Annapurna: The First Conquest of an 8,000-Meter Peak', {}],
      [u'meta', '', {u'content': 'cover', u'name': 'cover'}],
      [u'date', '2011-07-26T04:00:00+00:00', {}],
      [u'contributor',
       'calibre (1.22.0) [http://calibre-ebook.com]',
       {u'role': 'bkp'}],
      [u'identifier', '9781453226308', {u'scheme': 'ISBN'}],
      [u'identifier', 'B005DI8Y0C', {u'scheme': 'MOBI-ASIN'}],
      [u'identifier',
       '51565721-c619-42bc-957f-df0fcd6f6aa0',
       {u'id': 'uuid_id', u'scheme': 'uuid'}],
      [u'identifier',
       '51565721-c619-42bc-957f-df0fcd6f6aa0',
       {u'scheme': 'calibre'}],
      [u'subject', 'Mountaineering', {}]]
    """
    assert bool(fname)^bool(epub),"provide only one of fname/epub"
    if fname is not None:
            assert isinstance(fname, basestring), "filename isnt string"
            assert ope(fname), "filename doesnt exist"
            epub = Epub.from_file(fname)
    assert epub is not None, "need filename or epub obj"
    out = []
    for element in epub.metadata:
            tag_name = element.tag.localname
            tag_text = element.tag.text
            tag_contents = dict(element.tag.iteritems())
            out.append(EpubTag(
                name=tag_name,
                text=tag_text,
                extra=tag_contents))
    return out

def parse_tags_epub(tags):
    """ the output of get_tags_epub cannot be directly
        converted into a dictionary (stupid xml), but
        a subsection of it usually can.  this includes
        entries for things like title/subject/language
    """
    out = [ [tag.name, tag.text] for tag in tags if not tag.extra]
    out = dict(out)
    try:
        creator = [tag for tag in tags if tag.name=='creator'][0].text
    except IndexError:
        creator = 'unknown'
    author = creator
    isbn = [x for x in tags if x.is_isbn]
    isbn = isbn[0].text if isbn else ''
    if isbn:
        out.update(isbn=isbn)
    out.update(creator=creator,
               author=author,
               raw=str(tags))
    return out
