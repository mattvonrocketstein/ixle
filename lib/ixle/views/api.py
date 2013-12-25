""" ixle.views.api
"""
import json
from .widgets import Widget
from ixle.util import get_api
from report import report

class APIView(Widget):

    url = '/api'
    returns_json = True
    def main(self):
        arg   = self['_']
        action = self['action']
        # almost every api needs a path, except for
        # "fill()" which only needs a fieldname
        # assert path and action
        api = get_api()
        try:
            ackshun = api[action]
        except KeyError:
            error = 'no api-action found with name "{0}"'.format(action)
            self.flash(error)
            return dict(
                error=("APIView can't find an "
                       "api-action called {0}").format(action))
        print 'calling api with: ', ackshun, arg
        try:
            status = ackshun(arg)
        except Exception,e:
            import sys, traceback
            err_data = traceback.format_exc()
            print err_data
            return dict(error=err_data)

        #except Exception, e:
        #    report('encountered error running api command')
        #    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        #    status = str([ action, e ])
        self.flash('ran {0} on \'{1}\''.format(action, arg))
        #status = 'status: {0}'.format(status)
        #self.flash(status)
        print 'api returning json:', status
        return status

from corkscrew.comet import CometWorker

class APIC(CometWorker):

    url = '/apic'

    def worker(self, **kargs):
        import time
        arg   = kargs['_']
        action = kargs['action']
        # almost every api needs a path, except for
        # "fill()" which only needs a fieldname
        # assert path and action
        api = get_api()
        try:
            ackshun = api[action]
        except KeyError:
            error = 'no api-action found with name "{0}"'.format(action)
            print "FLASH: error " + (error)
            return dict(
                error=("APIView can't find an "
                       "api-action called {0}").format(action))
        print 'calling api with: ', ackshun, arg
        try:
            status = ackshun(arg)
        except Exception,e:
            import sys, traceback
            err_data = traceback.format_exc()
            print err_data
            return dict(error=err_data)

        #except Exception, e:
        #    report('encountered error running api command')
        #    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        #    status = str([ action, e ])
        print "FLASH"+('ran {0} on \'{1}\''.format(action, arg))
        #status = 'status: {0}'.format(status)
        #self.flash(status)
        print 'api returning json:', status
