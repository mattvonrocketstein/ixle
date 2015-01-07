""" ixle.heuristics.nlp

    natural language processing heuristics
"""
from collections import OrderedDict

import nltk

from ixle.python import ope
from .base import H, Heuristic
from ixle.schema import Item
from peak.util.imports import lazyModule

heuristics = lazyModule('ixle.heuristics')



class freq_dist(Heuristic):
    """ this heuristic returns a dictionary of {token:frequency}
        for this item whenever

          1) the item exists (or is mounted), AND
          2) the is_text(item) heuristic is true

        NOTE:
          this will require nltk and perhaps some of the nltk
          data, depending on how the distro ships things.
          if you seem to be missing tokenizers, try running
          this from console:

            >>> import nltk;
            >>> nltk.download('punkt')
            >>> nltk.download('treebank')

          alternatively it can be useful to do this manually
          with the GUI because that's the only way you'll
          get a statusbar on the download. use nltk.download()
          with no arguments and a gui will open.  click
          "All Packages", and find things from there.
    """
    apply_when = ['item_exists', 'is_text']

    def run(self):
        fdist = nltk.FreqDist()
        with open(self.item.path) as f:
            tmp=f.read()
            for sent in nltk.sent_tokenize(tmp.lower()):
                for word in nltk.wordpunct_tokenize(sent):
                    if word.isalnum():
                        fdist.inc(word)
        fdist = OrderedDict(fdist.items())
        return fdist

class vocabulary(Heuristic):
    apply_when = ['freq_dist']
    def run(self):
        return len(heuristics.freq_dist(self.item)().obj)
