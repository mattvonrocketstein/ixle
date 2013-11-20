""" ixle.heuristics.nlp

    natural language processing heuristics
"""
from collections import OrderedDict

import nltk

from ixle.python import ope

def freq_dist(item):
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
    from ixle.heuristics import is_text
    if not all([item.exists(), is_text(item)]):
        return {}
    fdist = nltk.FreqDist()
    with open(item.path) as f:
        tmp=f.read()
        for sent in nltk.sent_tokenize(tmp.lower()):
            for word in nltk.wordpunct_tokenize(sent):
                fdist.inc(word)
    fdist = OrderedDict(fdist.items())
    return fdist
