""" ixle.dsettings
    dynamic settings (stored in the database instead of .ini / cli)
"""
from report import report
from ixle.schema import DSetting

NAMES = [
    'ignore_patterns',
    'ignore_dirs',
    'random_sample_size'
    ]

DB_NAME = 'ixle_settings'
from ixle.util import get_or_create

def get_or_create_settings_database():
    return get_or_create(DB_NAME)

def dynamic_settings():
    db = get_or_create_settings_database()
    existing = [ DSetting.load(db, k) for k in db ]
    names = [ x._id for x in existing ]
    for expected_name in NAMES:
        if expected_name not in names:
            new_setting = DSetting(_id=expected_name)
            new_setting.store(db)
            existing.append(new_setting)
    tmp={}
    for x in existing:
        tmp[x._id] = x
    return tmp

def clean_dsettings(db=None):
    # remove old setting we no longer use
    pass
