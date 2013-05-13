""" ixle.views.agents
    NOTE: since it uses ajax, this is actually a widget
"""

from .base import View

class AgentView(View):
    url = '/_agents'
    template = '_agents.html'
    def main(self):
        from ixle.agents import registry
        return self.render(agents=registry)
