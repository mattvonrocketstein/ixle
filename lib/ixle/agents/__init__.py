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
from .tagger import Tagger
from .body import Body
from ._imdb import IMDBer, MovieFinder
from .space_killer import SpaceKiller
from .body import Body
#from .renamer import Renamer
from .slayer import Slayer

class AgentRegistry(dict):
    def register(self,name,kls):
        assert name not in self
        self[name] = kls

registry = AgentRegistry()

[ registry.register(x.nickname, x) for x in
  MovieFinder, IMDBer, Janitor, Body, #Renamer,
  SpaceKiller, Slayer,
  StaleChecker, Sizer, Filer, Mimer,
  Stamper, Typer, Events, Md5er, Indexer, Tagger ]
