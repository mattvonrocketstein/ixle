""" ixle.views.widgets

    ajaxy brickabrack
"""
from ixle.python import sep

from .base import View, BluePrint

class DirViewWidget(View):
    """
        example usage:
          /dir_view_widget?_=/media/sf_XMem/_MOVIES/Next.avi
    """
    url = '/dir_view_widget'
    blueprint = BluePrint(__name__, __name__)
    template = 'dir_view_widget.html'
    methods = 'GET POST'.split()

    def main(self):
        abspath = self['_']
        assert abspath
        abspath = abspath.split(sep)
        elements = abspath[:-1] # chop off fname
        tmp = []
        for i in range(len(elements)):
            component = elements[i]
            tmp.append([
                # ex: sf_XMem
                component,
                # ex: /media/sf_XMem/
                sep.join(elements[:i+1])])

        return self.render(path_elements=tmp)
