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
from ixle.heuristics.movies import *
from ixle.util import smart_split
from ixle.python import ope
from ixle.heuristics.data import CODE_EXTS
from .util import _generic
from .nlp import freq_dist

r_xx_min = re.compile('\d+ min')

# used for determining file_type, layer 1 specificity
r_crypto = [re.compile(_) for _ in
            ['.* private key.*',
             '.* public key.*',]]
r_text  = [ re.compile(_) for _ in
            ['.* text'] ]
r_video = [ re.compile(_) for _ in
            ['AVI', 'Flash Video', 'video: .*'] ]
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


def more_clean(item):
    # split on all kinds of nonalpha-numeric junk
    bits = smart_split(item.just_name.lower())

    # kill common junk that's found in torrent files, etc
    for x in 'cam dvdrip brrip eng xvid'.split():
        if x in bits: bits.remove(x)
    #remove 1080p, x264, etc
    bits2=[]
    for x in bits:
        if not any([
            re.compile('[a-zA-Z]\d+').match(x),
            re.compile('\d+[a-zA-Z]').match(x)]):
            bits2.append(x)
    bits = bits2
    result = '.'.join(['_'.join(bits),
                       item.fext or ''])
    # if original filename does not start with '_', neither
    # should the result.  (this happens with files like "[1]-foo-bar.mp3")
    one = re.compile('_+').match(item.fname)
    two = re.compile('_+').match(result)
    if not one and two:
        result = result[two.span()[-1]:]
    #for x in 'xvid'result = result.
    return result


def is_code(item):
    if item.fext not in CODE_EXTS:
        return False
    if item.file_type and item.file_type!='text':
        return False
    return True

def guess_genres(item):
    # should work on imdbd-movies that have already been tagged
    tmp = item.tags.get(
        'genres', # tagged movies
        item.tags.get('genre', []) # tagged audio
        )
    if not isinstance(tmp, list):
        tmp=[tmp]
    return tmp

def guess_mime(item):
    tmp = MIME_MAP.get(item.fext, None) or \
          item.mime_type
    if tmp and '/' in tmp:
        tmp = tmp[ : tmp.find('/')]
    return tmp

def guess_duration(item):
    # should work on imdbd-movies and songs
    if item.tags:
        runtime = item.tags.get('runtime', None) # imdb tags
        if runtime is not None:
            runtime = runtime[0]
            match = r_xx_min.match(runtime)
            if match:
                result = int(match.group().split()[0])
                return datetime.timedelta( minutes=result )

def is_crypto(item):  return _generic(item, r_crypto)
def is_text(item):  return _generic(item, r_text)
def is_video(item):
    return _generic(item, r_video) or \
               (FEXT_MAP.get(item.fext,None)=='video')

def is_audio(item): return _generic(item, r_audio)
def is_image(item): return _generic(item, r_image)

def is_tagged(item):
    """ """
    if item.tags: return True
    if item.file_magic:
        for entry in item.file_magic:
            if 'ID3' in entry:
                return True
