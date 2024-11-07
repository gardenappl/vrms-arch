import json
import os
import re
import sys

from pyparsing import Word, Literal, alphanums, infix_notation, opAssoc, Opt, ParseException, CaselessLiteral, ParseResults

src_dir = os.path.join(os.path.dirname(__file__), "..")
src_dir = os.path.realpath(src_dir)

with open(os.path.join(src_dir, "licenses.json")) as f:
    spdx_json = json.load(f)
    global SPDX_LICENSES, OSI_LICENSES, FSF_LICENSES, SPDX_VERSION, SPDX_DATE
    SPDX_VERSION = spdx_json["licenseListVersion"]
    SPDX_DATE = spdx_json["releaseDate"]
    SPDX_LICENSES = [license['licenseId'] for license in spdx_json['licenses']]
    OSI_LICENSES = [license['licenseId'] for license in spdx_json['licenses'] if license['isOsiApproved']]
    FSF_LICENSES = [license['licenseId'] for license in spdx_json['licenses'] 
                    if 'isFsfLibre' in license and license['isFsfLibre']]


spdx_simple = ((Word(alphanums, alphanums + '-' + '.') + Opt(Literal('+')) +
               Opt(Literal('WITH') + Word(alphanums, alphanums + '-' + '.'))))
spdx_complex = infix_notation(spdx_simple, [ (CaselessLiteral("AND"), 2, opAssoc.LEFT), 
                                             (CaselessLiteral("OR"), 2, opAssoc.LEFT) ])

def clean_license_name(license):
    license = license.lower()
    license = re.sub(r'(?:^custom:|[,\s_"/\(\)\:-])', '', license)
    license = re.sub('licence', 'license', license)
    return license


class LicenseFinder(object):
    def __init__(self):
        # number of packages
        self.num_pkgs = 0

        # all of the seen (clean) license names with counts
        self.by_license = {}

        # all of the seen (clean) license names with their raw variants
        self.license_names = {}

        # packages with "custom" license
        self.unknown_packages = set()

        # packages with a known non-free license
        self.nonfree_packages = set()

    def visit_db(self, db):
        pkgs = db.packages
        self.num_pkgs += len(db.packages)

        print("SPDX list version", SPDX_VERSION, "from", SPDX_DATE, file=sys.stderr)

        for pkg in pkgs:
            try_spdx = False

            # get a list of all licenses on the box
            for license in pkg.licenses:
                if " AND " in license.upper() or " OR " in license.upper() or " WITH " in license.upper():
                    try_spdx = True
                    break

            licenses = pkg.licenses
            if try_spdx:
                spdx_expression = " AND ".join(["({})".format(license) for license in pkg.licenses])
                try:
                    licenses = spdx_complex.parse_string(spdx_expression, parseAll=True)

                except ParseException:
                    print("Invalid SPDX expression:", spdx_expression, file=sys.stderr)

            # accepts list of licenses, possibly with 'AND', 'OR' and 'WITH' operators and sub-lists
            # if no operators are present, assume AND
            def check_license_list(licenses, free_criteria):
                and_expression = True

                with_clause = False
                found_any_free = False
                for item in licenses:
                    free = False
                    if isinstance(item, ParseResults):
                        free = check_license_list(item, free_criteria)
                    elif item.upper() == "AND" or with_clause:
                        continue
                    elif item.upper() == "WITH":
                        with_clause = True
                        continue
                    elif item.upper() == "OR":
                        and_expression = False
                        continue
                    else:
                        free = free_criteria(item)
                    if not free and and_expression:
                        return False
                    elif free:
                        found_any_free = True
                return found_any_free
            print("Package:", pkg.name)
            print("Licenses:", licenses)
            print("Is OSI?", check_license_list(licenses, lambda item: item in OSI_LICENSES))


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
        print("Packages of unknown license on this system: %d" % len(self.unknown_packages), file=sys.stderr)

        for upackage in sorted(self.unknown_packages, key=lambda pkg: pkg.name):
            print("%s: %s" % (upackage.name, upackage.licenses))

    def list_all_nonfree_packages(self):
        for nfpackage in sorted(self.nonfree_packages, key=lambda pkg: pkg.name):
            print("%s: %s" % (nfpackage.name, nfpackage.licenses))

        print("\nNon-free packages: %d (%.2f%% of total)\n" % (len(self.nonfree_packages),
            ((len(self.nonfree_packages) / float(self.num_pkgs)) * 100)), file=sys.stderr)

        if self.ethical_packages:
            self.list_all_ethical_packages(sys.stderr)

        print("\nThere are %d ambiguously licensed packages that vrms cannot certify." % len(self.unknown_packages), file=sys.stderr)
        print("Use --list-unknowns to list them (or --help for more info)",
              file=sys.stderr)

    def list_all_ethical_packages(self, file=sys.stdout):
        for epackage in sorted(self.ethical_packages, key=lambda pkg: pkg.name):
            print("%s: %s" % (epackage.name, epackage.licenses), file=file)

        print("\nPackages with ethical restrictions: %d" % len(self.ethical_packages), file=sys.stderr)
