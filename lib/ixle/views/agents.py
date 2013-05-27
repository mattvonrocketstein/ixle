""" ixle.views.agents
    NOTE: since it uses ajax, this is actually a widget
"""

from .widgets import Widget

class AgentView(Widget):

    url = '/_agents'

    template = '_agents.html'

    def main(self):
        from ixle.agents import registry
        return self.render(_=self['_'],
                           agents=registry)
