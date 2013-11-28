""" ixle.heuristics.base
"""

from ixle import util

class DumbWrapper(object):
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, x):
        return getattr(self.obj, x)

class Answer(DumbWrapper):
    def __str__(self):
        return "(Answer: {0})".format(str(self.obj))
    def __nonzero__(self):
        return bool(self.obj)
    __repr__ = __str__

class NotApplicable(DumbWrapper):
    def __nonzero__(self): return False
    def __str__(self):
        return "(NotApplicable: {0})".format(str(self.obj))

class Heuristic(object):
    apply_when = []
    is_heuristic = True
    NotApplicable = NotApplicable

    def __init__(self, item):
        self.item = item

    def __call__(self):
        for x in self.apply_when:
            h = util.get_heuristics()[x]
            result = h(self.item)
            if isinstance(result, Heuristic):
                result = result()
            if not bool(result):
                return NotApplicable("{0} is False".format(x))
        result = self.run()
        if not isinstance(result, DumbWrapper):
            result = Answer(result)
        return result

    def run(self):
        return "DefaultAnswer"

def H(fxn):
    fxn.is_heuristic = True
    return fxn
