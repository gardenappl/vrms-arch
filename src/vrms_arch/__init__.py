# If you consider the output of this program to be legal advice,
# you're insane.

import argparse
import os
import os.path
import pyalpm

# DFSG/OSI-approved licenses, and the various variants in naming them
# I see in my package database

from .license_finder import LicenseFinder
from .disambiguation import UnambiguousDb

def vrms():
    parser = argparse.ArgumentParser(description='Virtual Richard M. Stallman for Arch Linux Resources: enumerates non-free packages (that is to say, under licenses not considered by OSI, FSF, and/or the DFSG to be Free Software)')

    parser.add_argument("-g", "--global-repos",
                        action="store_true",
                        help="Check licenses in all packages in all synced repositories (might exclude the AUR!), rather than that of locally installed packages")
    parser.add_argument("-a", "--list-licenses",
                        action="store_true",
                        help="List all licenses")
    parser.add_argument("-e", "--list-ethical",
                        action="store_true",
                        help="List only non-free packages with 'ethical source' licenses")
    parser.add_argument("-u", "--list-unknowns",
                        action="store_true",
                        help="List packages of unknown license instead of non-free packages")
    parser.add_argument

    args = parser.parse_args()

    h = pyalpm.Handle("/", "/var/lib/pacman")

    dbs_to_visit = []

    if args.global_repos:
        for d in set(os.path.splitext(f)[0] for f in os.listdir("/var/lib/pacman/sync")):
            h.register_syncdb(d, 0)
        dbs_to_visit = h.get_syncdbs()
    else:
        # print("There are %d installed packages." % len(h.get_localdb()))
        dbs_to_visit.append(h.get_localdb())

    visitor = LicenseFinder()

    for db in dbs_to_visit:
        # print("Reading pacman DB: %s" % db.name, file=sys.stderr)
        db = UnambiguousDb(db)
        visitor.visit_db(db)

    if args.list_unknowns:
        visitor.list_all_unknown_packages()
    elif args.list_ethical:
        visitor.list_all_ethical_packages()
    elif args.list_licenses:
        visitor.list_all_licenses_as_python()
    else:
        visitor.list_all_nonfree_packages()
