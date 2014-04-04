""" ixle.heuristics.naming
"""
import re
from ixle.python import opj
from ixle.util import smart_split, post_and_redirect
from ixle.heuristics.movies import guess_movie_year
from .base import SuggestiveHeuristic
from goulash.cache import cached

JUNK_LIST = 'notv publichd 1080p bluray hdtv lol cam dvdrip brrip eng xvid'.split()


class rendermixin(object):
    def _render(self):
        out = []
        for x in self.run():
            if isinstance(x, self.NotApplicable):
                out.append(str(x))
                continue
            tmp = opj(self.item.dir, x)
            tmp2 = self.item.path.replace("'","\'")
            zoo = post_and_redirect('/rename', _=tmp2, suggestion=tmp)
            out.append('<a href="javascript:{0}">{1}</a>'.format(zoo, x))
        return "<br/>".join(out)

class more_correct(SuggestiveHeuristic, rendermixin):
    apply_when = ['is_book']

    def suggestion(self):
        suggestions = self.run()
        opts = ['<a href=#>{0}</a>'.format(x) for x in suggestions]
        return 'correcting the filename', self._render()

    #@cached('more_correct',1)
    def run(self):
        if not self.item.apply_heuristic('is_tagged'):
            return [self.NegativeAnswer("a book, but not tagged")]
        title = _basic_clean(self.item.tags.get('title','').strip())
        author = self.item.tags.get('author', '').strip()
        author = author.split()[0]
        author = _basic_clean(author)
        out = []
        if title and author:
            out.append("{0}__{1}{2}".format(title, author, self.item.fext))
            out.append("{0}__{1}{2}".format(author, title, self.item.fext))
        if title:
            out.append("{0}{1}".format(title, self.item.fext))
        return self.Answer(sorted(out+[x.lower() for x in out]))

    def suggestion_applicable(self):
        ans = self.run()
        return any(ans)

class more_clean(SuggestiveHeuristic, rendermixin):

    def suggestion_applicable(self):
        return any(self.run())

    def suggestion(self):
        suggestions = self.run()
        opts = ['<a href=#>{0}</a>'.format(x) for x in suggestions]
        return 'cleaning the filename', self._render()

    @cached('more_clean', 1)
    def run(self):
        """ FIXME: doesnt work well S02E03"""
        suggestions = []
        tmp = self.item.fname.lower().replace(' ', '_')
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
                    tmp  = '_'.join(tmp[:tmp.index(year)+1])
                    tmp += '.'+self.item.fext
                    suggestions.append(tmp)
        from .movies import R_SEASON_1_EPISODE_1
        found = R_SEASON_1_EPISODE_1.search(self.item.fname)
        if found is not None:
            split = R_SEASON_1_EPISODE_1.split(self.item.fname)
            split = [x for x in split if x]
            if split:
                tmp = "{0}{1}{2}".format(
                    split[0],
                    found.string[found.start():found.end()],
                    self.item.unipath.ext)
                tmp = [tmp, tmp.lower()]
                for suggestion in tmp:
                    if all([suggestion not in suggestions,
                            suggestion!=self.item.fname]):
                        suggestions.append(suggestion)
        return list(set(suggestions))

    def basic_clean(self):
        fname,fext = self.item.just_name.lower(),self.item.fext
        return _basic_clean(fname, fext)

def _basic_clean(fname, fext=''):
        # split on all kinds of nonalpha-numeric junk
        bits = smart_split(fname)

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
                           fext or ''])
        # if original filename does not start with '_', neither
        # should the result.  (this happens with files like "[1]-foo-bar.mp3")
        one = re.compile('_+').match(fname)
        two = re.compile('_+').match(result)
        if not one and two:
            result = result[two.span()[-1]:]
        #for x in 'xvid'result = result.
        if result == fname:
            return self.NotApplicable("already clean")
        return result
