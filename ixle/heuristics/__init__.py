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
from .base import SuggestiveHeuristic, DirHeuristic, item_exists, is_dir
from .util import run_heuristic, run_dir_heuristics,get_dir_suggestions, run_heuristics

from .siblings import guess_related_siblings
from .siblings import guess_proper_parent_folder

from .basics import (
    is_code, guess_mime, is_crypto, is_video,
    is_text, is_audio, is_image)

# used for determining file_type, layer 2 specificity
from .data import FEXT_MAP, MIME_MAP, r_xx_min
from .naming import more_clean

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


class DeleteDirectories(DirHeuristic, SuggestiveHeuristic):
    """
    """

    def run(self):
        results = []
        for subdir in self.item.unipath.listdir():
            if subdir.isdir() and not subdir.listdir():
                results.append(subdir)
        if results:
            return self.Affirmative("{0} empty subdirectories".format(len(results)))

    def suggestion(self):

        return 'directory should be deleted',(
            '<ul>' + \
            '<li><a href="javascript:{0}">Do it</a>'.format('#') + \
            '</ul>'
            )

class DeleteDirectory(DirHeuristic, SuggestiveHeuristic):
    def run(self):
        if 0 == len(self.item.unipath.listdir()):
            return self.Affirmative("nothing here!")

    def asdads_suggestion_applicable(self):
        from unipath import FSPath
        if is_dir(self.item)():
            if self.run():
                return True

    def suggestion(self):
        return None, (
            '<a href="javascript:{0}">Do it</a>'.format(
                post_and_redirect(
                    '/delete',
                    _=self.item.path,
                    _from='both',
                    dir=True,))
            )

def post_and_redirect(url, **kargs):
    dct = [ "{0}:'{1}'".format(k,v) for k,v in kargs.items()]
    dct = ','.join(dct)
    return "post_and_redirect('"+url+"', {" + dct + "});"

class FlattenDirectory(DirHeuristic, SuggestiveHeuristic):
    threshold = 3

    def run(self):
        thresh = self.threshold
        if 0 < len(self.item.unipath.listdir()) < thresh:
            return self.Affirmative("less than {0} items".format(thresh))

    def adsad_suggestion_applicable(self):
        return is_dir(self.item)() and self.run()

    def _render(self, item):
        return ("post_and_redirect('/collapse_dir', {_: '" + \
                item.path + "'})")

    def suggestion(self):

        return 'directory should be flattened',(
            '<ul>' + \
            '<li><a href="javascript:{0}">Move contents into parent</a>'.format(self._render(self.item)) + \
            '</ul>'
            )


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


class is_tagged(Heuristic):
    def run(self):
        if self.item.tags: return True
        if self.item.file_magic:
            for entry in self.item.file_magic:
                if 'ID3' in entry:
                    return True
