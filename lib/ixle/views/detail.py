""" ixle.views.detail """

from report import report
from ixle.views.base import View
from ixle.schema import Item

class ItemDetail(View):
    """ TODO: does not handle filenames with a '#' in them correctly """
    url = '/detail'
    template = 'item/detail.html'

    def get_current_item(self):
        k = self['_']
        if not k:
            return self.flask.render_template('not_found.html')
        item = Item.objects.get(path=k)
        if item is None:
            return self.flask.render_template('not_found.html', filename=k)
        return item

    def main(self):
        item = self.get_current_item()
        if not isinstance(item, Item): # not_found
            return item

        # TODO: should be api command
        # check for any requests to set specific fields back to nil
        reset_requests = [ x[len('reset_'):] \
                           for x in self.request.values.keys() \
                           if x.startswith('reset_') ]
        if reset_requests:
            # TODO: do this with api
            from ixle.agents import registry
            for field in reset_requests:
                setattr(item, field, None)
                for agent_kls in registry.values():
                    if field in getattr(agent_kls,'covers_fields', []):
                        report('reseting "{0}" covers with: {1}'.format(
                            field, agent_kls))
                        agent = agent_kls(
                            items=[],
                            settings=self.settings,)

                        result = agent.callback(
                            item=item, key=item.id)
                        report('got: ' + str(agent.record))
            self.save(item)
            self.flash('saved item: ' + str(self.record))
            return self.redirect(self.url+'?_='+self['_'])

        from ixle.util import get_heuristics
        heuristics = {}
        for fxn_name, fxn in get_heuristics().items():
            heuristics[fxn_name] = fxn(item)

        from ixle.agents import registry
        from ixle.util import get_api
        agents = list(set(registry.keys() + get_api().keys()))

        return self.render(item = item,
                           agents=agents,
                           query = self['_'],
                           heuristics = heuristics)
Detail=ItemDetail
