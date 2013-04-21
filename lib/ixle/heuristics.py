""" ixle.heuristics
"""
import re
from report import report

# used in guessing mime-type
MIME_MAP = dict(aa='audio', couch='data',
                view='data', sqlite='data',
                srt='text')

# used for determining file_type, layer 2 specificity
FEXT_MAP = dict(aa='audio',
                py='code',
                pub='crypto',
                rar='archive',
                zip='archive',
                gz='archive',
                exe='windows-executable',
                wma='windows-media',
                ogg='audio',
                m4a='audio',
                old='obsolete',
                bak='obsolete',
                flac='audio',
                pdf='document',
                txt='document',
                doc='document',
                view='database',
                couch='database',
                sqlite='database',
                srt='subtitles',
                idx='subtitles',
                m4v='video',
                sub='subtitles',
                db='database')
# used for determining file_type, layer 1 specificity
r_crypto = [re.compile(_) for _ in
            ['.* private key.*',
             '.* public key.*',
             ]]
r_text = [re.compile(_) for _ in
          ['.* text']]
r_video = [re.compile(_) for _ in
           ['AVI',
            'video: .*']]
r_audio = [re.compile(_) for _ in
           ['Audio file.*',
            'Microsoft ASF',
            'MPEG ADTS']]
r_image = [re.compile(_) for _ in
           ['JPEG .*',
            'GIF .*',
            'PNG .*']]

def guess_mime(item):
    return MIME_MAP.get(item.fext, None)

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
from couchdb.client import Row
def is_movie(item):
    """ answer whether this is perhaps a movie.
        "movie" is distinct from "video".. we want
        to guess whether this is a full length motion
        picture.
    """
    if isinstance(item,Row):
        item = Item.wrap(item)
    MOVIE_CUT_OFF_SIZE_IN_MB = 400
    report(item.abspath)
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
            return False
    return True
