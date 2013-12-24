""" ixle.views.base
"""

from corkscrew.views import BluePrint
from corkscrew import View as CorkscrewView
from ixle.agents.base import SaveMixin

from collections import defaultdict

class View(CorkscrewView, SaveMixin):
    def __init__(self, *args, **kargs):
        self.record = defaultdict(lambda:0)
        super(View, self).__init__(*args, **kargs)

    def render(self, *args, **kargs):
        if 'this_url' not in kargs:
            kargs.update(this_url=self.url)
        if '_' not in kargs and self['_']:
            kargs.update(_=self['_'])
        return super(View,self).render(*args, **kargs)

    @property
    def db(self):
        return self.settings.database
    database=db
