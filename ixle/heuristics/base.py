""" ixle.heuristics.base
"""

from ixle import util

class ListAnswerMixin(object):
    def render(self, result_list):
        out = []
        for x in result_list:
            out.append(str(x)+"<br/>")
        return ''.join(out)

class DumbWrapper(object):
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, x):
        return getattr(self.obj, x)

class Answer(DumbWrapper):
    def __str__(self):
        return "({0}: {1})".format(
            self.__class__.__name__,
            str(self.obj))

    def __nonzero__(self):
        return bool(self.obj)

    __repr__ = __str__

class NotApplicable(DumbWrapper):
    def __nonzero__(self):
        return False
    def __str__(self):
        return "(NotApplicable: {0})".format(str(self.obj))
    __repr__=__str__

class ExplainedAnswer(Answer):
    def __str__(self):
        return "({0}: {1})".format(
            self.__class__.__name__,
            str(self.explanation))

class Affirmative(ExplainedAnswer):
    def __init__(self, explanation="no reason given"):
        assert isinstance(explanation, basestring)
        self.obj = True
        self.explanation = explanation

    def __nonzero__(self):
        return True


class NegativeAnswer(ExplainedAnswer):
    def __init__(self, explanation="no reason given"):
        assert isinstance(explanation, basestring)
        self.obj = False
        self.explanation = explanation


class Heuristic(object):
    apply_when     = []
    require        = []
    is_heuristic   = True
    NotApplicable  = NotApplicable
    NegativeAnswer = NegativeAnswer
    Affirmative    = Affirmative
    Answer         = Answer

    def __init__(self, item):
        self.item = item
        self.category = self.__class__.__module__.split('.')[-1]

    def __str__(self):
        return "{0}::{1}".format(self.category, self.name)

    def suggestion_applicable(self):
        return False

    @property
    def name(self):
        return self.__class__.__name__

    def applicability(self):
        out = {}
        for x in self.apply_when:
            h = util.get_heuristics()[x]
            result = h(self.item)
            if isinstance(result, Heuristic):
                result = result()
            if not bool(result):
                result = NotApplicable("{0} is False".format(x))
            out[x] = result
        return out

    def __call__(self):
        for x in self.require:
            if not getattr(self.item, x):
                return NotApplicable("pre-req data not set: "+x)
        applicability = self.applicability()
        for name, result in applicability.items():
            if isinstance(result, NotApplicable):
                return result
        result = self.run()
        if not isinstance(result, DumbWrapper):
            result = Answer(result)
        return result

    def run(self):
        return "DefaultAnswer"

def H(fxn):
    fxn.is_heuristic = True
    return fxn

class SuggestiveHeuristic(Heuristic):

    def suggestion_applicable(self):
        """ by default the suggestion is applicable
            whenever the heuristic itself is
        """
        for name, result in self.applicability().items():
            if isinstance(result, NotApplicable):
                return False
        return True

    def suggestion(self):
        return 'preamble','html-option1 html-option2'.split()

class DirHeuristic(SuggestiveHeuristic):

    apply_when = ['is_dir']

    def __call__(self, *args, **kargs):
        if not self.item.unipath.isdir():
            return self.NotApplicable("Not a directory")
        return super(DirHeuristic,self).__call__(*args, **kargs)

class item_exists(Heuristic):
    def run(self):
        return self.item.exists()

class is_dir(Heuristic):
    def run(self):
        return self.item.unipath.isdir()
