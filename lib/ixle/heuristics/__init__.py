""" ixle.heuristics
"""
import re
from report import report

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
