""" ixle.agents """

from report import report

from .janitor import Janitor, StaleChecker
from .sizer import Sizer
from .filer import Filer
from .stamper import Stamper
from .typer import Typer, Mimer
from .dupes import Dupes
from .md5 import Md5er
from .indexer import Indexer
from .tagger import Tagger
from ._imdb import IMDBer

class AgentRegistry(dict):
    def register(self,name,kls):
        assert name not in self
        self[name] = kls

registry = AgentRegistry()
[ registry.register(x.nickname, x) for x in
  IMDBer, Janitor, StaleChecker, Sizer, Filer, Mimer,
  Stamper, Typer,Dupes, Md5er, Indexer, Tagger ]
