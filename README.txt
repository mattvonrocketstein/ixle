
Getting Started
================

Clone the repo and install pre-reqs:

  $ git clone git://github.com/mattvonrocketstein/ixle.git
  $ virtualenv node
  $ source node/bin/activate
  (node)$ pip install -r requirements.txt

Install and bootstrap ixle:

  (node)$ python setup.py develop
  (node)$ ixle -d # start couch daemon

Leave that last command running, do this in a different terminal:

  (node)$ ixle --install # setup couch databases
  (node)$ ixle           # start webserver

At this point you should be able to see the WUI @ http://localhost:5500

Unless you've done this all before, the database is empty right now.
Check out the "Examples" section below, and index some media.

Examples:
=========
  $ ixle --action=index /path/to/stuff

    Indexes everything under a certain directory;
    items already in the database will be skipped.

  $ ixle --force --action=index /path/to/stuff

    Force-index everything under a certain directory.
    Careful.. items already in the database will be overwritten.

  $ ixle --action=md5 /path/to/stuff

    Computes hashes for items in the database whenever the keys
    start with "/path/to/stuff".  (In other words this only works
    whenever the "index" action has already found a given file.)
    This won't recompute the hash if existing items already have
    that attribute set.  If you want to recompute, use --force

  $ ixle --action=file /path/to/stuff

WebUI QuickLinks:
=================

   * Couch info ( http://localhost:5500/_db )

        Shows total couchdb size and per-db length.
        Can also compact the databases.

   * Edit dynamic-settings ( http://localhost:5500/_settings )

        These are settings stored in couchdb (instead of the .ini).
        Use `ignore_patterns` to ignore filenames matching certain patterns
        Use `ignore_dirs` to mark certain directories as hands-off.
        Use `random_sample_size` to change item-count on ( http://localhost:5500/_random )
