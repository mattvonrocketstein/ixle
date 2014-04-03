""" ixle.views.file_viewer
"""

from report import report
from ixle.views.base import View
from .detail import ItemDetail
class Viewer(ItemDetail):
    """ TODO: check filesize first. """
    url      = '/view'
    template = 'item/viewer.html'
