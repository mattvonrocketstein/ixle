""" ixle.heuristics
"""
import re
from report import report
from ixle.schema import Item
from ixle.python import now
from ixle.util import smart_split

MOVIE_CUT_OFF_SIZE_IN_MB = 400

# used in guessing mime-type
MIME_MAP = dict(aa='audio', couch='data',
                view='data', sqlite='data',
                srt='text')
def guess_mime(item):
    return MIME_MAP.get(item.fext, None)

# used for determining file_type, layer 2 specificity
FEXT_MAP = dict(
    old='obsolete', bak='obsolete',
    gz='archive', zip='archive', rar='archive',
    txt='document', doc='document', pdf='document',
    m4a='audio', ogg='audio', flac='audio', aa='audio',
    idx='subtitles', sub='subtitles', srt='subtitles',
    db='database', sqlite='database', view='database', couch='database',
    js='code', py='code',
    pub='crypto',
    exe='windows-executable',
    m4v='video', wma='windows-media',)

# used for determining file_type, layer 1 specificity
r_crypto = [re.compile(_) for _ in
            ['.* private key.*',
             '.* public key.*',]]
r_text  = [ re.compile(_) for _ in
            ['.* text'] ]
r_video = [ re.compile(_) for _ in
            ['AVI', 'video: .*'] ]
r_audio = [ re.compile(_) for _ in
            ['Audio file.*','Microsoft ASF','MPEG ADTS'] ]
r_image = [ re.compile(_) for _ in
            ['JPEG .*', 'GIF .*','PNG .*'] ]


def _generic(item, r_list):
    # NOTE: assumes file_magic already ready
    if item.file_magic:
        for x in item.file_magic:
            for y in r_list:
                if y.match(x):
                    return True
    # else: use mimetype
def is_crypto(item):  return _generic(item, r_crypto)
def is_text(item):  return _generic(item, r_text)
def is_video(item): return _generic(item, r_video)
def is_audio(item): return _generic(item, r_audio)
def is_image(item): return _generic(item, r_image)

def is_tagged(item):
    """ """
    if item.file_magic:
        for entry in item.file_magic:
            if 'ID3' in entry:
                return True

def if_movie(fxn):
    def new_fxn(item):
        assert isinstance(item, Item)
        if not is_movie(item):
            report('not even a movie')
            return
        return fxn(item)
    return new_fxn

@if_movie
def guess_movie_year(item):
    numbers = []
    digits = re.compile('\d+')
    for x in smart_split(item.just_name):
        tmp = digits.match(x)
        if tmp and tmp.group()==x: numbers.append(x)
    numbers = [x for x in numbers if 1910 < int(x) < now().year ]
    if numbers:
        return numbers[0]


@if_movie
def guess_movie_name(item):
    year = guess_movie_year(item)
    if not year:
        # FIXME: not sure what to do yet.
        report('no movie year to split around')
        return
    bits = smart_split(item.just_name)
    before_year, after_year = (bits[:bits.index(year)],
                               bits[bits.index(year):])
    return ' '.join(before_year)

r_season_1_episode_1 = re.compile('.*[sS]\d\d*[eE]\d\d*.*')
def is_movie(item):
    """ answer whether this is perhaps a movie.
        "movie" is distinct from "video".. we want
        to guess whether this is a full length motion
        picture.
    """
    report(item.abspath)
    # clue: item is new in the database.. don't guess yet
    # clue: should be a video if it's going to be a movie..
    # clue: item is new in the database.. don't guess yet
    # clue: torrented tv shows that contain stuff S1E3 in the filename
    # clue: movies are pretty big
    if not item.file_type:
        report('file_type not set: ')
        return False
    if item.file_type!='video':
        report('not even a video.')
        return False
    if not item.size:
        report('size not set: ')
        return False
    if item.size_mb < MOVIE_CUT_OFF_SIZE_IN_MB:
        report('too small')
        return False
    if r_season_1_episode_1.match(item.fname):
        report('looks like a tv show.')
        return False
    if no_alphabet(item.just_name):
        report('probably from your digital camera')
        return False
    return True
