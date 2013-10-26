""" ixle.views.newest """

from report import report
from ixle.schema import Item
from ixle.views.search import ItemListView

class Newest(ItemListView):

    template = 'newest.html'
    url = '/newest'
    methods = 'get post'.upper().split()

    def get_queryset(self):
        return Item.objects.all().order_by("-t_seen")
