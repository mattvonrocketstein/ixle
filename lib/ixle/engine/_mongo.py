""" ixle.engine._mongo
"""
from .base import Engine
class MongoDB(Engine):
    def get_server(self):
        return MongoClient(self.settings['mongo']['server'],
                           self.settings['mongo']['port'])
