""" ixle.views.api
"""
import time, json
import sys, traceback
from .widgets import Widget
from ixle.util import get_api, isdir
from report import report
from corkscrew.comet import CometWorker

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
            error = 'no API action found with name "{0}"'.format(action)
            self.flash(error)
            return dict(
                error=("APIView can't find an "
                       "api-action called {0}").format(action))
        report('calling api with: ', ackshun, arg)
        try:
            status = ackshun(arg)
        except Exception,e:
            import sys, traceback
            err_data = traceback.format_exc()
            print err_data
            return dict(error=err_data)

        #except Exception, e:
        #    report('encountered error running api command')
        #    status = str([ action, e ])
        self.flash('ran {0} on \'{1}\''.format(action, arg))
        #status = 'status: {0}'.format(status)
        #self.flash(status)
        print 'api returning json:', status
        return status


class APIC(CometWorker):

    url = '/apic'

    def extra_html(self):
        """
        {%if is_dir%}
        <a href="/browser?_={{_}}">back to browsing</a>
        {%else%}
        <a href="/detail?_={{_}}">back to detail</a>
        {%endif%}
        """
        return self.render(
            self.extra_html.__doc__,
            is_dir=isdir(self['_']),
            _=self['_'],)

    def worker(self, **kargs):
        arg   = kargs['_']
        action = kargs['action']
        # almost every api needs a path, except for
        # "fill()" which only needs a fieldname
        # assert path and action
        api = get_api()
        try:
            ackshun = api[action]
        except KeyError:
            error = 'no API-action found with name "{0}"'.format(action)
            report("ERROR " + (error))
            return dict(
                error=("APIView can't find an "
                       "api-action called {0}").format(action))
        print 'calling api with: ', ackshun, arg
        try:
            status = ackshun(arg)
        except Exception,e:
            err_data = traceback.format_exc()
            print err_data
            return dict(error=err_data)

        #except Exception, e:
        #    report('encountered error running api command')

        #    status = str([ action, e ])
        print "FLASH"+('ran {0} on \'{1}\''.format(action, arg))
        #status = 'status: {0}'.format(status)
        #self.flash(status)
        print 'api returning json:', status
