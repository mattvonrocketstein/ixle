""" ixle.views.detail """

from .base import View
from ixle.schema import Item

class Detail(View):
    """ TODO: does not handle filenames with a '#' in them correctly """
    url = '/detail'
    template = 'item_detail.html'

    def get_current_item(self):
        k = self['_']
        if not k:
            return self.flask.render_template('not_found.html')
        item = Item.load(self.db, k)
        if item is None:
            return self.flask.render_template('not_found.html')
        return item

    def main(self):
        item = self.get_current_item()
        from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        if not isinstance(item, Item): # not_found
            return item
        # check for any requests to set specific fields back to nil
        reset_requests = [ x[len('reset_'):] \
                           for x in self.request.values.keys() \
                           if x.startswith('reset_') ]
        if reset_requests:
            for field in reset_requests:
                setattr(item, field, None)
            self.save(item)
            self.flash('saved item: '+self['_'])
            #self.redirect(..)
        from ixle.util import get_heuristics
        heuristics = {}
        for fxn_name, fxn in get_heuristics().items():
            heuristics[fxn_name] = fxn(item)
        return self.render(item = item,
                           query = self['_'],
                           heuristics = heuristics)
