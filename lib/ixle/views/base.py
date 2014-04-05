""" ixle.views.base
"""

from corkscrew import View as CorkscrewView
from ixle.agents.base import SaveMixin
from ixle.schema import Item
from collections import defaultdict

class View(CorkscrewView, SaveMixin):

    def __init__(self, *args, **kargs):
        self.record = defaultdict(lambda:0)
        super(View, self).__init__(*args, **kargs)

    def render(self, *args, **kargs):
        if '_' not in kargs and self['_']:
            kargs.update(_=self['_'])
        return super(View,self).render(*args, **kargs)

    @property
    def db(self):
        return self.settings.database
    database=db

    def get_current_item(self):
        k = self['_']
        if not k:
            return self.flask.render_template('not_found.html')
        item = Item.objects.get(path=k)
        if item is None:
            return self.flask.render_template('not_found.html', filename=k)
        return item
