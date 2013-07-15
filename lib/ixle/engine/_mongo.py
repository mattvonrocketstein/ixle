""" ixle.engine._mongo
"""
from .base import Engine
class MongoDB(Engine):
    def start_daemon(self):
        from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()

    def get_server(self):
        return MongoClient(self.settings['mongo']['server'],
                           self.settings['mongo']['port'])
