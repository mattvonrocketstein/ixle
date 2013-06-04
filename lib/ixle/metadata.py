""" ixle.metadata
"""

import configparser
from ixle.python import opj, ope, dirname, abspath

class IxleMetadata:
    ixle_home = dirname(__file__)
    ixle_config = opj(ixle_home, 'config')
    default_local_ini = abspath(opj(ixle_config, 'local.ini'))
    virgin_local_ini = abspath(opj(ixle_config, 'local.ini.original'))

    @property
    def couch_settings(self):
        if getattr(self, '_cp_couch_settings', None):
            return self._cp_couch_settings
        else:
            cp = configparser.ConfigParser()
            cp.read(self.default_local_ini)
            self._cp_couch_settings = cp
            return cp
metadata = IxleMetadata()
