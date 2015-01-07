""" ixle.dsettings
    dynamic settings (stored in the database instead of .ini / cli)
"""
from report import report
from ixle.schema import DSetting

FNAME_BLACKLIST = 'fname_blacklist'

NAMES = [
    # any indexed item with this fname will be deleted from fs & db
    FNAME_BLACKLIST,
    'bookmarks',
    'ignore_patterns',
    'ignore_dirs',
    'random_sample_size'
    ]

DB_NAME = 'ixle_settings'

from ixle.util import get_or_create

def get_or_create_settings_database():
    return get_or_create(DB_NAME)

def dynamic_settings():
    """ returns a dictionary of the dynamic settings """
    db = get_or_create_settings_database()
    existing = [s for s in DSetting.objects.all()]
    names = [ x.name for x in existing ]
    for expected_name in NAMES:
        if expected_name not in names:
            new_setting = DSetting(name=expected_name)
            new_setting.save()
            existing.append(new_setting)
    tmp={}
    for x in existing:
        tmp[x.name] = x
    return tmp

"""
class FnameBlackList(DSetting):
    setting_name = FNAME_BLACKLIST
    default_value = '[]'
    def decode(self):
        return super(FnameBlackList, self).decode() or json.loads(self.default_value)
"""
