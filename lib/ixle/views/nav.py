"""
"""
from .base import View
class Nav(View):
    url = '/_nav'
    template = 'navigation.html'
    def main(self):
        return self.render()
