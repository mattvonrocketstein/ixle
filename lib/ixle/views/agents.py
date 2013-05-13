"""
"""
from .base import View
class AgentView(View):
    url = '/_agents'
    template = '_agents.html'
    def main(self):
        from ixle.dsettings import NAMES
        return self.render(agents=registry)
