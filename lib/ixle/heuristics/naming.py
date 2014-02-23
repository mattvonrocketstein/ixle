""" ixle.heuristics.naming
"""
import re
from ixle.python import opj
from ixle.util import smart_split
from ixle.heuristics.movies import guess_movie_year
from .base import SuggestiveHeuristic

JUNK_LIST = 'hdtv cam dvdrip brrip eng xvid'.split()

class more_clean(SuggestiveHeuristic):

    @property
    def suggestion_applicable(self):
        return any(self.run())

    def suggestion(self):
        suggestions = self._run()
        opts = ['<a href=#>{0}</a>'.format(x) for x in suggestions]
        #return '<strong>|</strong>'.join(opts)
        return 'cleaning the filename', self._render('ignored')

    def _render(self, answer):
        out = []
        for x in self._cached_result:
            if isinstance(x, self.NotApplicable):
                out.append(str(x))
                continue
            tmp = opj(self.item.dir, x)
            tmp2 = self.item.path.replace("'","\'")
            zoo = link = "post_and_redirect('/rename', {_: '"+tmp2+"', suggestion:'"+tmp+"' })"
            #out.append('<a href="{0}">{1}</a>'.format(
            #        "/rename?_={0}&suggestion={1}".format(
            #            self.item.path,
            #            opj(self.item.dir,x)),x))
            out.append('<a href="javascript:{0}">{1}</a>'.format(zoo, x))
        return "<br/>".join(out)

    def _run(self):
        suggestions = []
        tmp = self.item.fname.lower().replace(' ','_')
        if tmp!=self.item.fname:
            suggestions.append(tmp)
        basic = self.basic_clean()
        suggestions.append(basic)
        if basic:
            movie_year = guess_movie_year(self.item)().obj
            if movie_year:
                tmp = smart_split(basic)
                year = str(movie_year)
                if year in tmp:
                    tmp = '_'.join(tmp[:tmp.index(year)+1])
                    tmp+='.'+self.item.fext
                    suggestions.append(tmp)
        self._cached_result = list(set(suggestions))
        return self._cached_result

    def run(self):
        return self._run()

    def basic_clean(self):
        # split on all kinds of nonalpha-numeric junk
        bits = smart_split(self.item.just_name.lower())

        # kill common junk that's found in torrent files, etc
        for x in JUNK_LIST:
            if x in bits: bits.remove(x)
        #remove 1080p, x264, etc
        bits2=[]
        for x in bits:
            if not any([
                re.compile('[a-zA-Z]\d+').match(x),
                re.compile('\d+[a-zA-Z]').match(x)]):
                bits2.append(x)
        bits = bits2
        result = '.'.join(['_'.join(bits),
                           self.item.fext or ''])
        # if original filename does not start with '_', neither
        # should the result.  (this happens with files like "[1]-foo-bar.mp3")
        one = re.compile('_+').match(self.item.fname)
        two = re.compile('_+').match(result)
        if not one and two:
            result = result[two.span()[-1]:]
        #for x in 'xvid'result = result.
        if result == self.item.fname:
            return self.NotApplicable("already clean")
        return result
