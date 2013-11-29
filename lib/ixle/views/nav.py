""" ixle.views.nav
"""
from .base import View
class Nav(View):
    url = '/_nav'
    template = 'navigation.html'
    methods = 'get post'.split()
    def main(self):
        from ixle.agents import registry
        from ixle.util import get_api
        agents = list(set(registry.keys() + get_api().keys()))
        agents.sort()
        return self.render(agents=agents)
