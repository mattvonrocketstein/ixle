""" ixle.heuristics.data
"""

document = 'document'

CODE_EXTS = 'py js cpp'.split()
BOOK_EXTS = 'epub'.split()
AUDIO_EXTS = 'aa'.split()

import re

r_xx_min = re.compile('\d+ min')

r_text  = [ re.compile(_) for _ in
            ['.* text'] ]

r_video = [ re.compile(_) for _ in
            ['AVI', 'Flash Video', 'video: .*'] ]

r_crypto = [re.compile(_) for _ in
            ['.* private key.*',
             '.* public key.*',]]
r_image = [ re.compile(_) for _ in
            ['JPEG .*', 'GIF .*','PNG .*'] ]

r_audio = [ re.compile(_) for _ in
            ['Audio file.*','Microsoft ASF','MPEG ADTS'] ]

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
