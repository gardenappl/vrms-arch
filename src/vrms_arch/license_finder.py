import json
import os
import sys

from pyparsing import Word, Literal, alphanums, infix_notation, opAssoc, Opt, ParseException, CaselessKeyword, Combine

from .disambiguation import filter_license_name

src_dir = os.path.join(os.path.dirname(__file__), "..")
src_dir = os.path.realpath(src_dir)

with open(os.path.join(src_dir, "licenses.json")) as f:
    spdx_json = json.load(f)
    global SPDX_LICENSES, OSI_LICENSES, FSF_LICENSES, SPDX_VERSION, SPDX_DATE
    global FILTERED_SPDX_LICENSES, FILTERED_OSI_LICENSES, FILTERED_FSF_LICENSES
    SPDX_VERSION = spdx_json["licenseListVersion"]
    SPDX_DATE = spdx_json["releaseDate"]
    SPDX_LICENSES = [license['licenseId'] for license in spdx_json['licenses']]
    FILTERED_SPDX_LICENSES = list(map(filter_license_name, SPDX_LICENSES))
    OSI_LICENSES = [license['licenseId'] for license in spdx_json['licenses'] if license['isOsiApproved']]
    FILTERED_OSI_LICENSES = list(map(filter_license_name, OSI_LICENSES))
    FSF_LICENSES = [license['licenseId'] for license in spdx_json['licenses'] 
                    if 'isFsfLibre' in license and license['isFsfLibre']]
    FILTERED_FSF_LICENSES = list(map(filter_license_name, FSF_LICENSES))


spdx_simple = (Combine(Word(alphanums, alphanums + '-' + '.') + Opt(Literal('+'))) +
               Opt(CaselessKeyword('WITH') + Word(alphanums, alphanums + '-' + '.')))
spdx_complex = infix_notation(spdx_simple, [ (CaselessKeyword("AND"), 2, opAssoc.LEFT), 
                                             (CaselessKeyword("OR"), 2, opAssoc.LEFT) ])


class LicenseFinder(object):
    def __init__(self):
        # number of packages
        self.num_pkgs = 0

        # all of the seen (clean) license names with counts
        self.by_license = {}

        # all of the seen (clean) license names with their raw variants
        self.license_names = {}

        # packages with a list of unknown licneses
        self.unknown_packages = {}

        # packages with a known non-free license
        self.nonfree_packages = set()

        print("SPDX list version", SPDX_VERSION, "from", SPDX_DATE, file=sys.stderr)

    def visit_db(self, db):
        pkgs = db.packages
        self.num_pkgs += len(db.packages)

        for pkg in pkgs:
            try_spdx = False

            # get a list of all licenses on the box
            licenses = pkg.licenses
            for license in licenses:
                if " AND " in license.upper() or " OR " in license.upper() or " WITH " in license.upper():
                    try_spdx = True
                    break

            is_spdx = False
            if try_spdx:
                spdx_expression = " AND ".join(["({})".format(license) for license in licenses])
                try:
                    licenses = spdx_complex.parse_string(spdx_expression, parseAll=True)
                    is_spdx = True

                except ParseException:
                    print(pkg.name, "- Expected SPDX expression but was invalid:", licenses, file=sys.stderr)

            # accepts list of licenses, with 'AND', 'OR' and 'WITH' operators and sub-lists
            # returns list of unsatisfied licenses
            def check_spdx_expression(licenses, free_criteria):
                or_expression = False

                with_clause = False
                found_any_free = False
                unfree_licenses = []
                for item in licenses:
                    free = False
                    if not isinstance(item, str):
                        unfree_licenses += check_spdx_expression(item, free_criteria)
                        free = len(unfree_licenses) == 0
                    else:
                        item_upper = item.upper()
                        if item_upper == "AND" or with_clause:
                            continue
                        elif item_upper == "WITH":
                            with_clause = True
                            continue
                        elif item_upper == "OR":
                            or_expression = True
                            continue
                        else:
                            free = free_criteria(item)
                        if not free:
                            unfree_licenses.append(item) 
                    if free:
                        found_any_free = True
                return [] if (or_expression and found_any_free) else unfree_licenses

            if is_spdx:
                unfree_licenses = check_spdx_expression(licenses, lambda item: item in SPDX_LICENSES)
            else:
                unfree_licenses = list(filter(lambda l: filter_license_name(l) not in FILTERED_SPDX_LICENSES, licenses))

            if len(unfree_licenses) > 0:
                # if is_spdx: print(pkg.name, "- not SPDX:", unfree_licenses)
                self.unknown_packages[pkg.name] = unfree_licenses


    # Print all seen licenses in a convenient almost python list
    def list_all_licenses_as_python(self):
        obscure_license_pop_cutoff = 7
        sorted_by_popularity = list(self.by_license.keys())
        sorted_by_popularity.sort(key=lambda lic : len(self.by_license[lic]), reverse=True)
        for lic in sorted_by_popularity:
            pop = len(self.by_license[lic])
            license_names = self.license_names[lic]
            license_name = max(license_names, key=license_names.get)
            print("    \"%s\",%s" % (license_name.replace("\"", "\\\""), " # %s" % [ p.name for p in self.by_license[lic] ] if pop < obscure_license_pop_cutoff else ""))

    def list_all_licenses(self):
        sorted_by_popularity = list(self.by_license.keys())
        sorted_by_popularity.sort(key=lambda lic : len(self.by_license[lic]), reverse=True)
        for lic in sorted_by_popularity:
            print("%s: %d" % (lic, len(self.by_license[lic])))

    def list_all_unknown_packages(self):
        print("Packages of unknown license on this system: %d" % len(self.unknown_packages.keys()), file=sys.stderr)

        sorted_packages = sorted(self.unknown_packages.keys())
        for package in sorted_packages:
            print("%s: %s" % (package, self.unknown_packages[package]))

    def list_all_nonfree_packages(self):
        for nfpackage in sorted(self.nonfree_packages, key=lambda pkg: pkg.name):
            print("%s: %s" % (nfpackage.name, nfpackage.licenses))

        print("\nNon-free packages: %d (%.2f%% of total)\n" % (len(self.nonfree_packages),
            ((len(self.nonfree_packages) / float(self.num_pkgs)) * 100)), file=sys.stderr)

        print("\nThere are %d ambiguously licensed packages that vrms cannot certify." % len(self.unknown_packages), file=sys.stderr)
        print("Use --list-unknowns to list them (or --help for more info)",
              file=sys.stderr)
