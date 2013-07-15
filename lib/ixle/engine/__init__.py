""" ixle.engine
"""
from ixle.engine._mongo import MongoDB
from ixle.engine._couch import CouchDB
engine = CouchDB() #MongoDB
