""" ixle.runner """
import socket
from report import report

from corkscrew.runner import flask

def restarting_runner_wrapper(*args, **kargs):
    """ overriding and chaining because
        restart should result in umount """
    go = lambda: flask(*args, **kargs)
    try:
        go()
    except socket.error:
        from ixle.schema import Remote
        Remote.umount_all()
        import time
        report('waiting for socket..')
        time.sleep(3)
        report("finished waiting, will retry")
        go()
