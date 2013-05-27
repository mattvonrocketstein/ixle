""" ixle.views.api
"""

from .widgets import Widget
from ixle.util import get_api

class APIView(Widget):

    url = '/api'

    def main(self):
        path = self['_']
        action = self['action']
        assert path and action
        api = get_api()
        try:
            ackshun = api[action]
        except KeyError:
            error = 'no api-action found with name "{0}"'.format(action)
            #self.flash(error)
            return '<font color=red>' + error + '</font>'
        try:
            status = ackshun(path)
        except Exception, e:
            status = str([ action, e ])
        self.flash('ran {0} on \'{1}\''.format(action, path))
        #status = 'status: {0}'.format(status)
        #self.flash(status)
        return '{0}'.format(status)
