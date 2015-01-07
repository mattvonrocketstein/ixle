""" ixle.agents.slayer
"""
from report import report
from ixle.python import ope
from .base import ItemIterator

from .base import DestructionMixin

class Slayer(ItemIterator, DestructionMixin):
    """ deletes items from disk AND from database."""

    DEBUG = True
    nickname = 'slayer'
    NO_COMMAND_LINE = True # TODO: enforce this

    def callback(self, item, fname=None, **kargs):
        self.delete_file(item=item)
