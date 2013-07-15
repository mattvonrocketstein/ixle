""" ixle.engine.base
"""
class Engine(object):
    def __init__(self):
        from ixle.settings import Settings
        self.settings = Settings()

    def __getitem__(self, name):
        return self.settings[name]
