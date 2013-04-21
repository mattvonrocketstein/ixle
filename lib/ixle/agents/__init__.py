""" ixle.agents """

from report import report

from .base import IxleAgent, IxleDBAgent,  KeyIterator, ItemIterator
from .janitor import Janitor, StaleChecker
from .sizer import Sizer
from .filer import Filer
from .stamper import Stamper
from .typer import Typer, Mimer
from .dupes import Dupes
from .md5 import Md5er
from .indexer import Indexer
from .tagger import Tagger

class AgentRegistry(dict):
    def register(self,name,kls):
        assert name not in self
        self[name] = kls

registry = AgentRegistry()
[ registry.register(x.nickname, x) for x in
  Janitor, StaleChecker, Sizer, Filer, Mimer,
  Stamper, Typer,Dupes, Md5er, Indexer, Tagger ]
