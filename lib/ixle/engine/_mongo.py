""" ixle.engine._mongo
"""
#from pymongo import MongoClient
#client = MongoClient()
class MongoDB(object):
    def get_server(self):
        return MongoClient('localhost', 27017)

