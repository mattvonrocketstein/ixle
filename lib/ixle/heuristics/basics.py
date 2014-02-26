""" ixle.heuristics.basics
"""
from .base import Heuristic
from .data import (
    CODE_EXTS, MIME_MAP,
    r_audio, r_crypto, r_video, r_text)

class is_code(Heuristic):
    apply_when = []
    requires = ["file_type"]
    def run(self):
        if self.item.fext not in CODE_EXTS:
            return self.NegativeAnswer(
                "\"{0}\" not in CODE_EXTS".format(self.item.fext))
        return True

class guess_mime(Heuristic):
    is_heuristic = True
    apply_when = []
    def run(self):
        tmp = MIME_MAP.get(self.item.fext, None) or \
              self.item.mime_type
        if tmp and '/' in tmp:
            tmp = tmp[ : tmp.find('/')]
        return tmp


class is_crypto(Heuristic):
    def run(self):
        return _generic(self.item, r_crypto)

class is_video(Heuristic):
    def run(self):
        if self.item.mime_type and self.item.mime_type.startswith('video'):
            return self.Affirmative('mime_type match')
        if _generic(self.item, r_video):
            return self.Affirmative('file_magic hint')
        if FEXT_MAP.get(self.item.fext, None)=='video':
            return self.Answer('FEXT_MAP rule')

class is_text(Heuristic):
    require = ['file_magic', 'mime_type']

    def run(self):
        if self.item.mime_type.startswith('text'):
            return self.Affirmative("based on mime_type")
        return _generic(self.item, r_text)

class is_audio(Heuristic):
    def run(self):
        tmp = guess_mime(self.item)()
        if tmp:
            return tmp
        else:
            return _generic(self.item, r_audio, AUDIO_EXTS)

class is_image(Heuristic):
    def run(self):
        return _generic(self.item, r_image)
