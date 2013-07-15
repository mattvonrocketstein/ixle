""" ixle.agents """

from report import report

from .janitor import Janitor, StaleChecker
from .sizer import Sizer
from .filer import Filer
from .stamper import Stamper
from .typer import Typer, Mimer
from .events import Events
from .md5 import Md5er
from .indexer import Indexer
from .tagger import MusicTagger, ImageTagger
from .body import Body
from ._imdb import IMDBer, MovieFinder
from .body import Body
#from .renamer import Renamer
from .slayer import Slayer

class AgentRegistry(dict):
    def register(self,name,kls):
        assert name not in self
        self[name] = kls

registry = AgentRegistry()

[ registry.register(x.nickname, x) for x in
  #heuristic record-rewriters
  MovieFinder, IMDBer,
  # filesystem-modifiers / heuristics record-rewriters
  #Renamer,
  # experimental
  Body, Events,
  # clean-up (major side-effects)
  StaleChecker, Janitor, Slayer,
  # core record-rewriters
  Sizer, Md5er, Filer, Mimer,
  Stamper, Typer,
  # the index stands alone
  Indexer,
  # adaptive-taggers
  ImageTagger, MusicTagger
  ]
