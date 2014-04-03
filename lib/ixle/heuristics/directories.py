""" ixle.heuristics.directories
"""
import re

from .base import is_dir
from ixle.python import opj
from ixle.util import post_and_redirect

from .base import DirHeuristic, SuggestiveHeuristic

class DeleteDirectories(DirHeuristic, SuggestiveHeuristic):
    """
    """

    def _empty_subdirs(self):
        results = []
        for subdir in self.item.unipath.listdir():
            if subdir.isdir() and not subdir.listdir():
                results.append(subdir)
        return results

    def run(self):
        results = self._empty_subdirs()
        if results:
            return self.Affirmative("{0} empty subdirectories".format(len(results)))

    def suggestion(self):
        results = self._empty_subdirs()
        html = '<ul>'
        for fpath in results:
            link = post_and_redirect(
                '/delete', _=str(opj(fpath,'')), is_dir=1, _from='fs')
            html += '<li><a href="javascript:{0}">{1}</a>'.format(link, fpath)
        html+='</ul>'
        return 'these (empty) directories should be deleted', html

class DeleteDirectory(DirHeuristic, SuggestiveHeuristic):
    def run(self):
        if 0 == len(self.item.unipath.listdir()):
            return self.Affirmative("nothing here!")

    def asdads_suggestion_applicable(self):
        from unipath import FSPath
        if is_dir(self.item)():
            if self.run():
                return True

    def suggestion(self):
        return None, (
            '<a href="javascript:{0}">Do it</a>'.format(
                post_and_redirect(
                    '/delete',
                    _=self.item.path,
                    _from='both',
                    dir=True,))
            )


class CleanDirectory(DirHeuristic,SuggestiveHeuristic):
    def _find_torrent_junk(self):
        regex = [ re.compile('.*SAMPLE.*',re.IGNORECASE),
                  re.compile('.*ownload.*\.txt$',re.IGNORECASE),
                  re.compile('.*\.nfo$', re.IGNORECASE),
                  ]
        results=[]
        for fname in self.files:
            for rx in regex:
                if rx.match(fname):
                    results.append(fname)
                    break
        return results

    def run(self):
        return self._find_torrent_junk() #+ self._find_samples()

    def _render(self, fname):
        return post_and_redirect('/delete', _=fname, _from='both')

    def suggestion(self):
        results = self.run()
        out = '<ul>'
        for fpath in results:
            out+='<li><a href="javascript:{0}">{1}</a>'.format(
                self._render(str(fpath)), fpath.name)
        out+='</ul>'
        return 'removing files:',out

class FlattenDirectory(DirHeuristic, SuggestiveHeuristic):

    threshold = 3

    def run(self):
        thresh = self.threshold
        if 0 < len(self.files) < thresh:
            return self.Affirmative("less than {0} items".format(thresh))

    def _render(self, item):
        return ("post_and_redirect('/collapse_dir', {_: '" + \
                item.path + "'})")

    def suggestion(self):

        return 'directory should be flattened',(
            '<ul>' + \
            '<li><a href="javascript:{0}">Move contents into parent</a>'.format(self._render(self.item)) + \
            '</ul>'
            )
