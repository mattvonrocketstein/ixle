""" ixle.heuristics.siblings
"""

from goulash.cache import cached

from ixle.util import smart_split
from .base import ListAnswerMixin, Heuristic
from .base import SuggestiveHeuristic


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

    @property
    def suggestion_applicable(self):
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        if len(self.siblings) > 1:
            sample = self.siblings[0]
            for folder in self._suggest_folder_name:
                if sample.unipath.parent.endswith(folder):
                    return False
            return True

    @cached('guess_siblings')
    def suggestion(self):
        """ """
        from jinja2 import Template
        from ixle.util import sanitize_txt
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
