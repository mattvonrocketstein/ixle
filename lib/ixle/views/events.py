""" ixle.views.events
"""
from ixle.schema import Item, Event

from .base import View

class Events(View):
    url = '/events'
    template = 'events.html'

    def main(self):
        if self['clear_all']:
            # TODO: ask
            Event.objects.all().delete()
            return self.redirect(self.url)
        return self.render(items=Event.objects.all())
