""" ixle.heuristics
"""
import re
import datetime
from report import report
from ixle.heuristics.movies import *
from ixle.util import smart_split
# used in guessing mime-type
MIME_MAP = dict(part='data',
                aa='audio', couch='data',
                view='data', sqlite='data',
                srt='text')

def more_clean(item):
    bits = smart_split(item.just_name.lower())
    for x in 'xvid'.split():
        if x in bits: bits.remove(x)
    result = '.'.join(['_'.join(bits),
                       item.fext])
    #for x in 'xvid'result = result.
    return result

def is_code(item):
    return all([item.fext in 'py js'.split(),
                item.file_type=='text'])

def guess_genres(item):
    # should work on imdbd-movies that have been
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


r_xx_min = re.compile('\d+ min')

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

# used for determining file_type, layer 2 specificity
FEXT_MAP = dict(
    part='partial-file',
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
    if item.tags: return True
    if item.file_magic:
        for entry in item.file_magic:
            if 'ID3' in entry:
                return True
