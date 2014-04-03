""" ixle.agents.tagger
"""

import mutagen
from report import report
from ixle.schema import Item
from ixle.agents.base import ItemIterator
from ixle.util import get_heuristics, call_agent_on_item
from .util import hachm, clean_tags
from ixle import api

class AbstractTagger(ItemIterator):
    def callback(self, item=None, **kargs):
        from ixle.exceptions import FileDoesntExist
        if not item.exists():
            err = 'item does not exist: ' + item.fname
            self.report_error(err)
            return dict(error=FileDoesntExist(err))

    def callback(self, *args, **kargs):
        raise Exception, 'Subclassers should override!'

class GenericTagger(AbstractTagger):
    nickname='tagger'
    covers_fields = ['tags']
    DEBUG = True
    heuristics = get_heuristics()

    def _using(self, kls):
        call_agent_on_item(kls.nickname, self._item)
        self.record['tagged_with_{0}'.format(kls.__name__)] += 1

    def callback(self, item=None, **kargs):
        #sooper = super(GenericTagger, self).callback(item=item, **kargs)
        if False:
            pass
        else:
            self._item = item
            if self.heuristics['is_image'](item)():
                self._using(ImageTagger)
            elif self.heuristics['is_audio'](item)():
                self._using(MusicTagger)
            elif self.heuristics['is_book'](item)():
                self._using(BookTagger)
            else:
                self.record['cannot_tag'] += 1

class BookTagger(AbstractTagger):
    nickname = 'book_tagger'
    covers_fields = [] # only generictagger should do this..

    def callback(self, item=None, **kargs):
        path = item.unipath
        assert path.exists(),'does not exist!'
        assert path.endswith('epub'), 'not implemented for non-epub'
        from ixle.util.epub import get_tags_epub, parse_tags_epub
        tags = get_tags_epub(path)
        tags = parse_tags_epub(tags)
        item.tags = tags
        self.save(item)

class ImageTagger(AbstractTagger):
    nickname = 'itagger'
    covers_fields = [] # only generictagger should do this..

    def callback(self, item=None, **kargs):
        m = hachm(item.path)
        if m:
            m=dict(m)
        else: m={}
        item.tags = m
        self.save(item)

class MusicTagger(AbstractTagger):
    nickname = 'mtagger'
    covers_fields = [] # only generictagger should do this..

    def _query_override(self):
        # deprecated?
        if not self.path:
            return Item.objects.filter(fext__in=['mp3'])

    def callback(self, item=None, **kargs):
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
                    item.tags = clean_tags(item.tags)
                    self.save(item)
            else:
                self.report_status(
                    "file exists but cannot open"
                    " mutagen File object.. is this a music file?")
