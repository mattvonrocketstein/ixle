""" ixle.agents._imdb
"""
import urllib
from urllib2 import urlopen, HTTPError

import demjson
from report import report

from ixle.heuristics import is_movie
from ixle.query import javascript
from ixle.agents.base import ItemIterator
from ixle import heuristics

class IMDBApi(object):
    def __init__(self, title, year=None):
        query = dict(q=title)
        if year is not None: query.update(year=year)
        self.url = 'http://imdbapi.org/?{0}'.format(
            urllib.urlencode(query))

    def __call__(self):
        try:
            fhandle = urlopen(self.url)
        except HTTPError,e :
            report('caught an error.. call back later? '+str(e))
            return []
        contents = fhandle.read()
        api_result = demjson.decode(contents)
        if isinstance(api_result, dict) and 'error' in api_result:
            report("api_result is bad: "+str(api_result))
            return []
        #if self.year:
        #    matches = []
        #    for possible_match in api_result:
        #        match_year = int(possible_match['year'])
        #        if match_year == int(self.year):
        #            matches.append(possible_match)
        #else:
        matches = api_result
        return matches

class IMDBer(ItemIterator):
    nickname = 'imdb'

    def __init__(self, *args, **kargs):
        super(IMDBer,self).__init__(*args, **kargs)
        assert not self.path, 'i cant use a path'

    @property
    def query(self):
        return javascript.find_equal(fieldname='file_type',
                                     value='video')

    def callback(self, item=None, **kargs):
        if not heuristics.is_movie(item):
            return
        if any([self.force, not item.tags]):
            report(item.fname)
            name,year = [heuristics.guess_movie_name(item),
                         heuristics.guess_movie_year(item)]
            report('extracted: '+str([name, year]))
            api_obj = IMDBApi(name, year=year)
            matches = api_obj()
            if not matches:
                report('no matches for this search: '+str([name,year]))
            elif len(matches)>1:
                report('multiple matches for this search: '+str([name,year]))
                from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
            elif len(matches)==1:
                match = matches[0]
                item.tags=match
                self.save(item)
