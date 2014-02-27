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
from ixle.heuristics.data import CODE_EXTS, AUDIO_EXTS
from .nlp import freq_dist, vocabulary
from .base import H, Heuristic, Answer, NegativeAnswer, ListAnswerMixin
from .base import SuggestiveHeuristic
from ixle.util import get_heuristics

from .siblings import guess_related_siblings
from .siblings import guess_proper_parent_folder

from .basics import (
    is_code, guess_mime, is_crypto, is_video,
    is_text, is_audio, is_image)

# used for determining file_type, layer 2 specificity
from .data import FEXT_MAP, MIME_MAP
from .naming import more_clean

r_xx_min = re.compile('\d+ min')

# used for determining file_type, layer 1 specificity

def _generic(item, r_list, extensions={}):
    """ NOTE: assumes file_magic already ready already"""
    if item.fext in extensions:
        return Heuristic.Affirmative("file-extension hint-hit: "+item.fext)
    if item.file_magic:
        for x in item.file_magic:
            for y in r_list:
                if y.match(x):
                    return Answer(True)
        return NegativeAnswer("file_magic doesnt match")
    return NegativeAnswer("not enough data")

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

def run_heuristics(item) :
    results = {}
    for fxn_name, fxn in get_heuristics().items():
        results.update(run_heuristic(fxn_name,item))
        #result = fxn(item)
        #if isinstance(result, Heuristic):
        #    result1 = result()
        #results[result] = result1
    return results
