""" ixle.dsettings
    dynamic settings (stored in the database instead of .ini / cli)
"""
from report import report
from ixle.schema import DSetting

NAMES = [
    'ignore_patterns',
    'ignore_dirs',
    ]

DB_NAME = 'ixle_settings'

def get_or_create_settings_database():
    from ixle.settings import Settings
    server = Settings().server
    if DB_NAME not in server:
        server.create(DB_NAME)
    db = server[DB_NAME]
    return db

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
