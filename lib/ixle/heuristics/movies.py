""" ixle.heuristics.movies
"""
import re

from report import report

from ixle.python import now
from ixle.schema import Item
from ixle.util import smart_split, no_alphabet
from .base import Heuristic

MOVIE_CUT_OFF_SIZE_IN_MB = 400
r_season_1_episode_1 = re.compile('.*[sS]\d\d*[eE]\d\d*.*')

def if_movie(fxn):
    def new_fxn(item):
        assert isinstance(item, Item)
        if not is_movie(item):
            report('not even a movie')
            return
        return fxn(item)
    new_fxn.__name__ = fxn.__name__
    return new_fxn



@if_movie
def guess_movie_name(item):
    def pop_junk(list_of_words):
        out = []
        FORBIDDEN = 'eng cd1 cd2'.split()
        for x in list_of_words:
            if x.lower() not in FORBIDDEN:
                out.append(x)
        return out
    year = guess_movie_year(item)
    if not year:
        # FIXME: not sure what to do yet.
        report('no movie year to split around')
        return
    bits = smart_split(item.just_name)
    before_year, after_year = (bits[:bits.index(year)],
                               bits[bits.index(year)+1:])
    guess = ' '.join(before_year)
    if not guess: # empty when left-of-year is empty
        guess = ' '.join(pop_junk(after_year))
    return guess

def is_movie(item):
    """ answer whether this is perhaps a movie.
        "movie" is distinct from "video".. we want
        to guess whether this is a full length motion
        picture.
    """
    # clue: item is new in the database.. don't guess yet
    # clue: should be a video if it's going to be a movie..
    # clue: item is new in the database.. don't guess yet
    # clue: torrented tv shows that contain stuff S1E3 in the filename
    # clue: movies are pretty big
    if no_alphabet(item.just_name):
        return False
    return True

class is_movie(Heuristic):
    apply_when = ["is_video"]
    require = ['file_size']

    def run(self):
        if 'video' not in self.item.mime_type:
            return self.NegativeAnswer(
                "mime_type doesn't mention video")
        if self.item.size_mb < MOVIE_CUT_OFF_SIZE_IN_MB:
            return self.NegativeAnswer(
                "size < {0}".format(MOVIE_CUT_OFF_SIZE_IN_MB))
        if r_season_1_episode_1.match(self.item.fname):
            return False
        return True

def _guess_movie_year(fname):
    numbers = []
    digits = re.compile('\d+')
    bits = smart_split(fname)
    for x in bits:
        tmp = digits.match(x)
        if tmp and tmp.group()==x:
            numbers.append(x)
    numbers = [x for x in numbers if 1910 < int(x) <= now().year ]

    if numbers:
        return numbers[0]

class guess_movie_year(Heuristic):
    apply_when = ['is_movie']
    def run(self):
        return _guess_movie_year(self.item.just_name)
