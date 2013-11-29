""" ixle.agents.elaborate
"""
from report import report
from ixle.python import ope
from .base import ItemIterator
from ixle.schema import Item
from ixle import util
from ixle import api

report = util.report

class Elaborate(ItemIterator):
    nickname = 'elaborate'

    def __call__(self, *args, **kargs):
        return super(Elaborate, self).__call__(*args, **kargs)

    def callback(self, item, fname=None, **kargs):
        for field_name, agent in util.agent_cover().items():
            if not getattr(item, field_name):
                report("elaborating '{0}' in {1}".format(
                    field_name, item.fname))
                agent_obj = util.call_agent_on_item(agent.nickname, item)
                #self.save(item)
        return

#report_if(item.fname)
        if not item.md5:
            if not item.exists():
                self.complain_missing(item.path)
                return
            result = self.run_and_collect(
                'md5sum "' + item.path + '"')
            try:
                result = result.split()[0]
            except:
                report('error collecting output from md5sum')
                self.record['count_errors'] += 1
            else:
                item.md5 = result
                report(item.fname + '  ' + result)
                self.save(item)
