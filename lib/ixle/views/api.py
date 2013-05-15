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
        ackshun = api[action]
        try:
            status = ackshun(path)
        except Exception, e:
            status = str(e)
        self.flash('ran {0} on "{1}"'.format(action, path))
        self.flash('status: {0}'.format(status))
        from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        return self.redirect('/')