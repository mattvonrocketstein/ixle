""" ixle.agents._imdb
"""
from ixle.heuristics import is_movie
from ixle.agents.base import ItemIterator

class IMDBer(ItemIterator):
    nickname = 'imdb'

    def __init__(self, *args, **kargs):
        super(IMDBer,self).__init__(*args, **kargs)
        assert not self.path, 'i cant use a path'

    @property
    def query(self):
        return is_empty_query('imdb')

    def callback(self, item=None, **kargs):
        pass
