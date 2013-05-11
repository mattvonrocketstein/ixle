""" ixle.views.base
"""

from corkscrew.views import BluePrint
from corkscrew import View as CorkscrewView
from ixle.agents.base import SaveMixin

class View(CorkscrewView, SaveMixin):
    def __init__(self, *args, **kargs):
        if self.__class__.blueprint is None:
            self.__class__.blueprint = BluePrint(self.__class__.__name__,
                                                 self.__class__.__name__)
        super(View, self).__init__(*args, **kargs)

    def render(self, *args, **kargs):
        if 'this_url' not in kargs:
            kargs.update(this_url=self.url)
        return super(View,self).render(*args, **kargs)

    @property
    def db(self):
        return self.settings.database
    database=db

    @property
    def dupes_db(self):
        return self.settings.dupes_db
