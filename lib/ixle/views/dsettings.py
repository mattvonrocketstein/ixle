""" ixle.views.dsettings
"""

from ixle.views.base import View
from ixle.schema import DSetting

class CorkscrewSettingsView(View):
    # TODO: abstract this back to corkscrew
    url = '/_settings'
    template = '_settings.html'
    methods = 'GET'.split()

class SettingsView(CorkscrewSettingsView):

    methods = 'GET POST'.split()

    def handle_post(self):

        name = self['name']
        assert name
        value = self['value']
        value = None if value in ['None', ''] else value
        setting = DSetting.objects.get(name=name)
        assert setting
        setting.value = value
        setting.save()
        return "ok"

    def main(self):
        if self['name']: self.handle_post()
        from ixle.dsettings import dynamic_settings, DB_NAME
        tmp = dynamic_settings()
        dsettings = tmp.values()
        for doc in dsettings:
            doc.edit_url = self.settings.server.document_url(
                DB_NAME, doc.id)
        return self.render(
            dsettings=dsettings,
            settings=self.settings,
            )

class AppendSetting(SettingsView):

    url = '/_settings/append/'

    methods = 'POST'.split()

    def main(self):
        back = self['back'] or SettingsView.url
        name = self['name']
        value = self['value']
        setting = DSetting.objects.get(name=name)
        v = setting.value
        #if not isinstance(v, (type(None), list)):
        #    self.flash("cannot append to nonlist tuple")
        #else:
        if isinstance(v, (type(None), list)):
            v = v or []
            v.append(value)
        if isinstance(v, basestring):
            # fix delim assumption
            v+=','+value
        setting.value = v
        setting.save()
        self.flash("saved: "+str(v))
        return self.redirect(back)
