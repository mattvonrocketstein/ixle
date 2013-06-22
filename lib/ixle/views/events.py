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
            self.events_db.delete_all(really = True)
        edb = Event.db()
        records = [ Event.load(edb, k) \
                    for k in edb.keys() ]
        return self.render(items=records)
