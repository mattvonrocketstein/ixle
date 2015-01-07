""" ixle.tests.common
"""
import os
import datetime
from ixle.schema import Item
def _(x):
    return datetime.datetime.strptime(x,"%Y-%m-%dT%H%M:%S:%fZ")

def make_item(main, **overrides):
    for field,value in main.items():
        if field.startswith('t_'):
            try:
                main[field] = _(value)
            except:
                pass
    item = Item(**main)
    for field,value in overrides.items():
        setattr(item, field, value)
    return item


def make_tv(**kargs):
    return make_item(
        {'id':('/media/sf_XMem/_TV/Game.of.Thrones.S02/'
               'Game.of.Thrones.S02E10.HDTV.x264-ASAP.Valar.Morghulis.mp4'),
         u'file_magic': [u'ISO Media', u'MPEG v4 system', u'version 1'],
         u't_last_mod': _('2013-02-18T00:56:05Z'), u'fext': u'mp4',
         u't_mod': _('2013-02-18T00:56:05Z'),
         u'file_type': u'video',
         u't_last_seen': _('2013-04-21T12:29:03Z'),
         u'fname': u'Game.of.Thrones.S02E10.HDTV.x264-ASAP.Valar.Morghulis.mp4',
         u't_seen': _('2013-04-21T12:29:03Z'),
         u'md5': u'432c6ed0032bb6aca12a30ad102b2065',
         u'mime_type': u'video/mp4', u'size': 467156},
        **kargs)

def make_mp3():
    return Item(
        _id = ('/media/sf___INCOMING/janewise/'
               'MAD-HOP - Mad-Hop vol.4/MAD-HOP'
               ' - Mad-Hop vol.4 - 01 Pixelord - Mad-Hop World.mp3'),
        file_magic= [u'Audio file with ID3 version 2.3.0', u'contains:'],
        t_seen= _('2013-04-20T12:08:48Z'), fext= u'mp3',
        file_type= u'audio',
        t_mod= _('2013-04-20T12:08:48Z'),
        t_last_seen= _('2013-04-21T12:30:41Z'),
        fname= u'MAD-HOP - Mad-Hop vol.4 - 01 Pixelord - Mad-Hop World.mp3',
        t_last_mod= _('2012-02-15T20:59:58Z'),
        md5= u'b4cc14e11857180d82dc26db9711826f',
        mime_type= u'audio/mpeg',
        size= 6812)

def make_movie(**kargs):
    default = ('/media/sf_XMem/_MOVIES/Network.1976.DVDRip.XviD/Network.1976.DVDRip.XviD.avi')
    key1 = kargs.pop('id', default)
    return make_item(
        dict(
            id=key1,
            fname= os.path.split(key1)[-1],
            file_magic = ['RIFF (little-endian) data',
                          'AVI', '608 x 336', '23.98 fps',
                          'video: XviD',
                          'audio: MPEG-1 Layer 3 (stereo',
                          '32000 Hz)'],
            t_last_seen= None,
            t_last_mod= None,
            t_seen= None,
            t_mod= None,
            fext= 'avi',
            file_type= 'video',
            mime_type= 'video/x-msvideo',
            md5= 'c3d516c081d0536883a04447985dd772',
            size=716288),
                    **kargs)

def make_subtitles():
    key2 = ('/media/sf_XMem/_MOVIES/Network.1976.DVDRip.XviD/'
            'Network.1976.DVDRip.XviD.srt')
    return Item(
        _id = key2,
        file_magic= ['ASCII English text', 'with CRLF line terminators'],
        fext= 'srt', fname= 'Network.1976.DVDRip.XviD.srt',
        file_type= 'subtitles', t_last_seen= None,
        t_seen= None, t_mod=None, t_last_mod=None,
        md5= '58f41a511690002cbf9bd8a4437d66fb',
        mime_type='text', size=108)
