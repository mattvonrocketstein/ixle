Examples:
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
