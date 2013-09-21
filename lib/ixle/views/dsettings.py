""" ixle.views.dsettings
"""

from ixle.views.base import View

class SettingsView(View):
    url = '/_settings'
    template = '_settings.html'
    methods = 'GET POST'.split()

    def handle_post(self):
        name = self['name']
        assert name
        value = self['value']
        value = None if value in ['None',''] else value
        from ixle.schema import DSetting
        setting = DSetting.objects.get(name=name)
        assert setting
        setting.value=value
        setting.save()
        return "ok"

    def main(self):
        if self['name']: self.handle_post()
        from ixle.dsettings import dynamic_settings, DB_NAME
        tmp = dynamic_settings()
        settings = tmp.values()
        for doc in settings:
            doc.edit_url = self.settings.server.document_url(
                DB_NAME, doc.id)
        return self.render(
            settings=settings)
