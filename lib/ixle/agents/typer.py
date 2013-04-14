from mimetypes import guess_type

from .base import ItemIterator

class Typer(ItemIterator):
    def callback(self, item=None, **kargs):
        changed = False
        if not item.mime_type:
            typ, encoding = guess_type(item.id)
            item.mime_type = typ
            print typ, item.id
            changed = True
        if not item.file_type:
            # wat do?
            pass
        if changed:
            self.save(item)
