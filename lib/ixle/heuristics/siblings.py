""" ixle.heuristics.siblings
"""

import os
from goulash.cache import cached as _cached

from jinja2 import Template
from ixle.python import opj
from ixle.util import smart_split
from ixle.util import sanitize_txt
from .base import ListAnswerMixin, Heuristic
from .base import SuggestiveHeuristic

# default cache timeout is too big
cached = lambda name: _cached(name, 8)

def _guess_parent(item):
    """ find a folder name in the
        same directory as this file
    """
    import editdistance
    from collections import defaultdict, OrderedDict
    matches = []
    assert item.unipath.exists()
    scores = defaultdict(lambda : 0)
    dirs = [ [x, smart_split(x.name.lower())] \
             for x in item.unipath.parent.listdir() if x.isdir()]
    dirs = dict(dirs)
    norm_name = smart_split(item.fname.lower())

    for d in dirs:
        scores[d]=editdistance.eval(norm_name, dirs[d])
    scores = [[x,y] for x,y in scores.items() if y!=0]
    winners = sorted(scores, cmp=lambda x,y: cmp(x[1],y[1]))[:3]
    winners = OrderedDict([ [ str(x[0]), x[1]] for x in winners])
    return winners

class guess_proper_parent_folder(#ListAnswerMixin,
                                 SuggestiveHeuristic):
    """ """
    def suggestion_applicable(self):
        return True

    def run(self):
        return str(_guess_parent(self.item))

    def suggestion(self):
        out=[]
        for x in _guess_parent(self.item):
            link = "post_and_redirect('/rename',{_:'" + \
                   self.item.path + "', suggestion:'"+ \
                   opj(x, self.item.fname)+"'})"
            link = '"javascript:' + link + '"'
            out.append('<a href={link}>{name}</a>'.format(link=link, name=x))

        #out = _guess_parent(self.item)
        js = """<script></script>"""
        return ['moving file to folder',
                js + 'Choose folder: '+'<strong> | </strong>'.join(out)]

def _guess_related_siblings(item):
    """ finds file names in the same directory
        that start off as suspiciously similar to
        the given <item>
    """
    matches = []
    siblings = item.siblings_from_db()
    tokens = smart_split(item.fname)
    for bro in siblings:
        if len(tokens[0]) > 3:
            comparison = smart_split(bro.fname)
            if comparison[0]==tokens[0]:
                matches.append(bro)
    return matches

class guess_related_siblings(ListAnswerMixin, SuggestiveHeuristic):
    """ """
    @property
    def siblings(self): return self._siblings()

    @cached('siblings')
    def _siblings(self):
        return _guess_related_siblings(self.item)

    @property
    def _suggest_folder_name(self):
        """ constructed by combining
            initial tokens (assumed to be common)
            from existing file names
        """
        tmp = self.siblings
        matches = []
        if tmp:
            zoo = smart_split(tmp[0].fname)
            for x in [0, 1]:
                try:
                    matches.append( '_'.join(zoo[:x+1]))
                except IndexError:
                    pass
        return matches

    def suggestion_applicable(self):
        """ """
        # guess whether repackaging into
        # a new folder is worthwhile
        if len(self.siblings) > 1:
            # guess whether it's already inside
            # the type of folder we would be suggesting
            sample = self.siblings[0]
            folders = self._suggest_folder_name
            for folder in folders:
                if sample.unipath.parent.endswith(folder):
                    return False
            # guesses a measurement as to whether the
            # directory is already well organized
            tmp=[x.fname for x in self.siblings]
            count=0
            fnames=os.listdir(sample.unipath.parent)
            for fname in fnames:
                if fname in tmp:
                    count+=1
            zult = count*1.0/len(fname)
            if zult > .80:
                return False
            return True

    @cached('guess_siblings')
    def suggestion(self):
        """ """
        out = []
        sanitized_name = sanitize_txt(self.item.fname)
        js_fxn_name = "repackage__{0}".format(sanitized_name)
        template = """
        <script>
        function repackage__{{sanitized_name}}(new_dir){
          console.debug("posting to repackage: {{sanitized_name}}");
          var siblings = [{%for sib in siblings%}
          "{{sib.path}}"{%if not loop.last%},{%endif%}
          {%endfor%}];
          var data = {'root_dir':'{{root_dir}}', 'new_dir':new_dir, siblings:siblings};
          console.debug(data);
          post_and_redirect('/repackage',data);
        }
        </script>"""
        t = Template(template)
        js = t.render(root_dir=self.item.dir,
                      sanitized_name=sanitized_name,
                      siblings=self.siblings)
        for x in self._suggest_folder_name:
            link = '"javascript:{js_fxn_name}(\'{new_dir}\')"'.format(
                js_fxn_name=js_fxn_name, new_dir=x)
            out.append('<a href={link}>{name}</a>'.format(link=link,name=x))
        return ['moving each file to a common subdirectory. ',
                js + 'Choose dir-name: '+'<strong> | </strong>'.join(out)]

    def run(self):
        matches = self.siblings
        return [ item.fname for item in matches ]
