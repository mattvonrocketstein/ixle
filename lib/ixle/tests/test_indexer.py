""" ixle.tests.test_indexer
"""
import sys
from unittest2 import TestCase

from ixle.util import report
from ixle.agents import Indexer
from ixle.settings import TestSettings as Settings
from ixle.exceptions import FileDoesntExist
class TestIndexer(TestCase):

    def setUp(self):
        self.test_file='/a/b/c'

    def test_nonsense_path(self):
        try:
            indexer = Indexer(settings=Settings(), path=self.test_file)
        except FileDoesntExist, e:
            pass
        else:
            raise Exception,'nonsense path accepted cheerfully by indexer'

    def test_is_ignored(self):
        indexer = Indexer(settings=Settings(), path='/')
        assert not indexer.is_ignored(self.test_file)
