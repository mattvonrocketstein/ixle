"""
"""
from .base import View

class _DB(View):
    methods = 'GET POST'.split()
    url = '/_db'
    template = '_db.html'

    def wrapper(self,db):
        return type('asdads',
                    (object,),
                    dict(
                        name=db,
                        edit_url=self.settings.server.edit_url(db)))

    def main(self):
        db = None
        if self['_'] or self['size']:
            db = self.settings.server[ self['_'] or self['size'] ]
        if self['size']:
            size = len(db)
            return str(size)
        if self['compact']:
            db.compact()
            return 'compacted'
        return self.render(
            db=self.wrapper(db),
            db_name=self['_'],
            dbs = [])# self.wrapper(x) for x in self.settings.server])
