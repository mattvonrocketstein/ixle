""" ixle.agents.refresh
"""

from ixle.agents.indexer import Indexer
from ixle.agents.janitor import StaleChecker

from ixle.agents.base import IxleAgent

class CompoundAgent(IxleAgent):
    """ Simple agent that executes one or more
        agents in certain sequence.  The agents
        involved should all take the same init
        arguments
    """
    subagents = []

    def __init__(self, *args, **kargs):
        self.my_init = [args,kargs]
        super(CompoundAgent, self).__init__(*args,**kargs)

    def __call__(self):
        args, kargs = self.my_init
        for Agent in self.subagents:
            agent = Agent(*args, **kargs)
            agent()

class Refresher(CompoundAgent):
    """ deletes records that correspond to
        nonexistent files, then reindex.
    """
    requires_path = True
    nickname = 'refresh'
    subagents = [StaleChecker, Indexer]
