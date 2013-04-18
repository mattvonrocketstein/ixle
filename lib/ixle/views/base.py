""" ixle.views.base
"""

from corkscrew.views import BluePrint
from corkscrew import View as CorkscrewView

class View(CorkscrewView):

    def render(self, *args, **kargs):
        if 'this_url' not in kargs:
            kargs.update(this_url=self.url)
        return super(View,self).render(*args, **kargs)

    @property
    def db(self):
        return self.settings.database

    @property
    def dupes_db(self):
        return self.settings.dupes_db
