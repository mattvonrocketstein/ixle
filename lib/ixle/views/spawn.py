""" ixle.views.spawn
"""
import threading
from flask import flash, redirect
from report import report
from ixle.agents import registry
from .base import View

class Spawn(View):
    """ spawn agent on a given path.

        this is a interstitial url right now mainly..
        people come here from /browser

    """
    url = '/spawn'
    template = 'spawn.html'
    methods = "GET POST".split()
    def main(self):
        force = True if self['force'] else False
        agent = self['agent']
        path = self['path']
        if agent and path:
            try:
                kls = registry[agent]
            except KeyError:
                flash("Unknown agent")
                return self.render(path=path, agent='')
            kargs = dict(settings=self.settings,
                         path=path, force=force)
            agent = kls(**kargs)
            report('created agent type {0} with kargs={1}'.format(
                agent.__class__.__name__,
                str(kargs)))
            t = threading.Thread(target=agent)
            t.start()
            flash("started agent in thread; redirecting to browser")
            return redirect('/browser?_='+path)
        return self.render(path=path,
                           agent=agent)
