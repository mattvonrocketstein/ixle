""" ixle.agents._imdb
"""
import urllib
from urllib2 import urlopen, HTTPError

import demjson
from report import report

from ixle.heuristics import is_movie
from ixle.agents.base import ItemIterator
from ixle import heuristics

from rottentomatoes import RT
rotten="d6jcrfycr3msyw7p27xth52r"
import copy
class IMDBApi(object):
    def __init__(self, title, year=0):
        self.query = dict(title=title, year=int(year))
        self.rt = RT(rotten)

    def __call__(self):
        matches = []
        year = self.query['year']
        results = self.rt.search(self.query['title'])
        self.partial = copy.copy(results)
        if year:
            results = [x for x in results if x['year']==self.query['year']]
        for r in results:
            matches.append(self.rt.info(r['id']))
        return matches

class MovieFinder(ItemIterator):
    nickname = 'moviefinder'
    covers_fields = ['is_movie']
    def callback(self, item=None, **kargs):
        out = heuristics.is_movie(item)
        item.is_movie = bool(out() or False)
        if item.is_movie:
            report('found movie: ' + item.fname)
        self.save(item)

class IMDBer(ItemIterator):
    nickname = 'imdb'
    #fix generictagger first
    #covers_fields = ['tags']
    def __init__(self, *args, **kargs):
        super(IMDBer,self).__init__(*args, **kargs)
        self.moviefinder = self.subagent(MovieFinder)
        #assert not self.path, 'i cant use a path'

    #def _query_override(self):
    #   2 versions:
    #     could rely on is_movie=True or just file_type='video'

    def callback(self, item=None, **kargs):
        self.moviefinder.callback(item=item)
        report(item.fname)
        if not item.is_movie:
            return
        if any([self.force, not item.tags]):
            report(item.fname)
            name, year = [ heuristics.movies._guess_movie_name(item.fname),
                           heuristics.movies._guess_movie_year(item.fname)]
            report('extracted: '+str([name, year]))
            api_obj = IMDBApi(name, year=year)
            report("Querying RT api..")
            matches = api_obj()
            if not matches:
                self.report_status(
                    'no matches for this search: ' + str([name,year]))
            elif len(matches)>1:
                self.report_status(
                    'multiple matches for this search: ' + str([name,year]))
                #raise Exception, NotImplemented
            elif len(matches)==1:
                match = matches[0]
                item.tags=match
                self.save(item)
