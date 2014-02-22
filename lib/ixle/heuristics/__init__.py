""" ixle.heuristics

    IMPORTANT:

        heuristics operate on Item objects, and have no side-effects.
        in general they determine "best-guesses" for questions like
        "is the file represented by this Item a movie?".  heuristics
        should be small and fairly fast (md5'ing a file is not considered
        fast).

        rather than doing some cumbersome registration procedure for heuristics,
        all heuristics will be mined out of this file based on whether they are
        callable and whether the first argument's name is "item".
"""

import re
import datetime
from report import report
from jinja2 import Template
from ixle.heuristics.movies import *
from ixle.util import smart_split
from ixle.python import ope, opj
from ixle.heuristics.data import CODE_EXTS
from .nlp import freq_dist, vocabulary
from .base import H, Heuristic, Answer, NegativeAnswer, ListAnswerMixin
from .base import SuggestiveHeuristic
from ixle.util import get_heuristics

def _generic(item, r_list):
    # NOTE: assumes file_magic already ready already
    if item.file_magic:
        for x in item.file_magic:
            for y in r_list:
                if y.match(x):
                    return Answer(True)
        return NegativeAnswer("file_magic doesnt match")
    return NegativeAnswer("not enough data")
r_xx_min = re.compile('\d+ min')

# used for determining file_type, layer 1 specificity
r_crypto = [re.compile(_) for _ in
            ['.* private key.*',
             '.* public key.*',]]
r_audio = [ re.compile(_) for _ in
            ['Audio file.*','Microsoft ASF','MPEG ADTS'] ]
r_image = [ re.compile(_) for _ in
            ['JPEG .*', 'GIF .*','PNG .*'] ]

# used for determining file_type, layer 2 specificity
document = 'document'
FEXT_MAP = dict(
    part='partial-file',
    old='obsolete', bak='obsolete',
    gz='archive', zip='archive', rar='archive',
    txt=document, doc=document, pdf=document,
    epub=document,mobi=document, # books
    m4a='audio', ogg='audio', flac='audio', aa='audio',
    idx='subtitles', sub='subtitles', srt='subtitles',
    db='database', sqlite='database', view='database', couch='database',
    js='code', py='code',
    pub='crypto',
    exe='windows-executable',
    flv='video',
    m4v='video', wma='windows-media',)

# used in guessing mime-type
MIME_MAP = dict(part='data',
                aa='audio',
                couch='data',
                view='data',
                sqlite='data',
                srt='text')
from .naming import more_clean

class is_code(Heuristic):
    apply_when = []
    requires = ["file_type"]
    def run(self):
        if self.item.fext not in CODE_EXTS:
            return self.NegativeAnswer(
                "\"{0}\" not in CODE_EXTS".format(self.item.fext))
        return True

class guess_genres(Heuristic):
    is_heuristic = True
    apply_when = ['is_tagged']
    def run(self):
        # should work on imdbd-movies that have already been tagged
        tmp = self.item.tags.get(
            'genres', # tagged movies
            self.item.tags.get('genre', []) # tagged audio
            )
        if not isinstance(tmp, list):
            tmp=[tmp]
        return tmp

class guess_mime(Heuristic):
    is_heuristic = True
    apply_when = []
    def run(self):
        tmp = MIME_MAP.get(self.item.fext, None) or \
              self.item.mime_type
        if tmp and '/' in tmp:
            tmp = tmp[ : tmp.find('/')]
        return tmp


class guess_duration(Heuristic):
    is_heuristic = True
    apply_when   = ["is_tagged"]
    def _from_mutagen(self):
        duration = self.item.tags.get('duration')
        if duration is not None:
            duration = duration.split('_')
            return ' '.join(duration)

    def _from_imdb(self):
        runtime = self.item.tags.get('runtime', None)
        if runtime is not None:
            result = runtime
            #match = r_xx_min.match(runtime)
            #if match:
            #    result = int(match.group().split()[0])
            return datetime.timedelta( minutes=result )

    def run(self):
        # should work on imdbd-movies and songs
        return self._from_imdb() or self._from_mutagen()

class is_crypto(Heuristic):
    def run(self):
        return _generic(self.item, r_crypto)

class is_text(Heuristic):
    r_text  = [ re.compile(_) for _ in
                ['.* text'] ]
    require = ['file_magic', 'mime_type']

    def run(self):
        if self.item.mime_type.startswith('text'):
            return self.Affirmative("based on mime_type")
        return _generic(self.item, self.r_text)

class is_video(Heuristic):
    r_video = [ re.compile(_) for _ in
                ['AVI', 'Flash Video', 'video: .*'] ]
    def run(self):
        if self.item.mime_type and self.item.mime_type.startswith('video'):
            return self.Answer('mime_type match')
        if _generic(self.item, self.r_video):
            return self.Answer('file_magic hint')
        if FEXT_MAP.get(self.item.fext,None)=='video':
            return self.Answer('FEXT_MAP rule')

from .siblings import guess_related_siblings

class is_audio(Heuristic):
    def run(self):
        return _generic(self.item, r_audio)

class is_image(Heuristic):
    def run(self):
        return _generic(self.item, r_image)

class item_exists(Heuristic):
    def run(self):
        return self.item.exists()

class is_tagged(Heuristic):
    def run(self):
        if self.item.tags: return True
        if self.item.file_magic:
            for entry in self.item.file_magic:
                if 'ID3' in entry:
                    return True

def run_heuristic(hname, item):
    h = get_heuristics()[hname](item)
    return {h:h()}

def run_heuristics(item):
    results = {}
    for fxn_name, fxn in get_heuristics().items():
        results.update(run_heuristic(fxn_name,item))
        #result = fxn(item)
        #if isinstance(result, Heuristic):
        #    result1 = result()
        #results[result] = result1
    return results
