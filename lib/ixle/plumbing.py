""" ixle.plumbing
"""

from hammock.plumbing import before_request as hbr

def before_request():
    hbr()
    #from ixle.engine._mongo import connect;
    #connect()
