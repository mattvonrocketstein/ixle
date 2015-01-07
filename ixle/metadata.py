""" ixle.metadata
"""


from ixle.python import opj, ope, dirname, abspath

class IxleMetadata:
    ixle_home = dirname(__file__)
    ixle_config = opj(ixle_home, 'config')
    # cocuchdb
    default_local_ini = abspath(opj(ixle_config, 'mongodb.conf'))
    #virgin_local_ini = abspath(opj(ixle_config, 'local.ini.original'))
metadata = IxleMetadata()
