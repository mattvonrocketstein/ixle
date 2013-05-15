""" ixle.views.widgets

    ajaxy brickabrack
"""
from ixle.python import sep, ope

from .base import View, BluePrint
class Widget(View):
    methods = 'GET POST'.split()

class IsAvailable(Widget):
    """ answers whether this file exists currently """
    url = '/widgets/is_available'
    def main(self):
        abspath = self['_']
        if abspath and ope(abspath):
            return ''
        return ('<small><font style="color:red;margin-left:15px;">'
                '(this file is not available.  is the drive mounted?)'
                '</font></small>')

class DirViewWidget(Widget):
    """
        example usage:
          /dir_view_widget?_=/media/sf_XMem/_MOVIES/Next.avi
    """
    url = '/dir_view_widget'
    blueprint = BluePrint(__name__, __name__)
    template = 'dir_view_widget.html'


    def main(self):
        abspath = self['_']
        assert abspath
        abspath = abspath.split(sep)
        is_dir = self['is_dir']
        if not is_dir: elements = abspath[:-1] # chop off fname
        else: elements = abspath
        tmp = []
        for i in range(len(elements)):
            component = elements[i]
            tmp.append([
                # ex: sf_XMem
                component,
                # ex: /media/sf_XMem/
                sep.join(elements[:i+1])])

        return self.render(path_elements=tmp)
