""" ixle.agents._imdb
"""

import re
from mimetypes import guess_type
from .base import ItemIterator

class IMDBer(ItemIterator):
    def __init__(self, *args, **kargs):
        super(IMDBer,self).__init__(*args, **kargs)
        assert not self.path, 'i cant use a path'

    @property
    def query(self):
        return is_empty_query('imdb')z
    def callback(self, item=None, **kargs):
