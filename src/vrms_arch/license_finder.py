import pyalpm
import re
import sys

def clean_license_name(license):
    license = license.lower()
    license = re.sub('(?:^custom:|[,\s_"/\(\)\:-])', '', license)
    license = re.sub('licence', 'license', license)
    return license

AMBIGUOUS_LICENSES = [clean_license_name(license) for license in [
    "custom",
    "other",
    "unknown",
    # CCPL (Creative Commons) should be specified with one of the
    # sublicenses (one of /usr/share/licenses/common/CCPL/*), some of
    # which are non-free
    "Creative Commons",
    "CCPL",
]]

FREE_LICENSES = [clean_license_name(license) for license in [
    'AFL-3.0',
    'AGPL',
    'AGPL3',
    'AGPL-3.0-only',
    'AGPL-3.0-or-later',
    'Apache',
    'Apache2',
    'Apache 2.0',
    'Apache 2.0 with LLVM Exception',
    'Apache License (2.0)',
    'Arphic Public License',
    'Artistic',
    'Artistic 2.0',
    'Beerware',
    'bitstream-vera',
    'Boost',
    'BSD',
    'BSD2',
    'BSD-2-clause',
    'BSD-2-Clause-Patent',
    'BSD3',
    'BSD-3-clause',
    'BSD License',
    'BSD-like',
    'BSDL',
    'BSD-style',
    'BSL',
    'bzip2',
    'CC0',
    'CC0 1.0',
    'CC-BY-3.0',
    'CC-BY-SA',
    'CC-BY-SA-2.5',
    'CC-BY-SA-3.0',
    'CC BY-SA-4.0',
    'CCPL:by',
    'CCPL:by-sa',
    'CCPL:cc-by',
    'CCPL:cc-by-sa',
    'CDDL',
    'CeCILL',
    'CPL',
    'Creative Commons, Attribution 3.0 Unported',
    'custom:free',
    'dumb',
    'EDL',
    'EDL-1.0',
    'EPL',
    'EPL-1.1',
    'EPL-2.0',
    'etpan',
    'EUPL-1.1',
    'EUPL-1.2',
    'ex',
    'Expat',
    'FDL',
    'FDL1.2',
    'FDL1.3',
    'FFSL',
    'FIPL',
    'font embedding exception',
    'FSFAP',
    'GD',
    'GFDL',
    'GFDL-1.1-no-invariants-or-later',
    'GFDL-1.2-only',
    'GFDL-1.2-no-invariants-only',
    'GFDL-1.3-or-later',
    'GFL',
    'GPL',
    'GPL-1.0-or-later',
    'GPL2+',
    'GPL2',
    'GPL-2.0+',
    'GPL-2.0',
    'GPL-2.0-only',
    'GPL-2.0-or-later',
    'GPL-2.0-or-later with GCC-exception-2.0 exception',
    'GPL2-only',
    'GPL2-or-later',
    'GPL2 or any later version',
    'GPL2 with OpenSSL exception',
    'GPL3',
    'GPL-3.0',
    'GPL-3.0-only',
    'GPL-3.0-or-later',
    'GPL3+GPLv2',
    'GPL3-only',
    'GPL3-or-later',
    'GPL3 or any later version',
    'GPL/BSD',
    'GPL+FE',
    'GPLv2+',
    'GPLv2',
    'GPLv3',
    'HPND',
    'IBM Public Licence',
    'icu',
    'ImageMagick',
    'Info-ZIP',
    'INN',
    'ISC',
    'isc-dhcp',
    'JasPer2.0',
    'Khronos',
    'LGPL',
    'LGPL2',
    'LGPL-2.0-only',
    'LGPL-2.0-or-later',
    'LGPL2.1+',
    'LGPL2.1',
    'LGPL2_1',
    'LGPL-2.1-only',
    'LGPL-2.1-or-later',
    'LGPL3',
    'LGPLv3+',
    'LGPL-3.0',
    'LGPL-3.0-only',
    'LGPL-3.0-or-later',
    'libpng',
    'libtiff',
    'libxcomposite',
    'LLGPL',
    'LPPL',
    'lsof',
    'MirOS',
    'MIT',
    'MIT-style',
    'MIT/X',
    'MITX11',
    'Modified BSD',
    'MPL',
    'MPL2',
    'MPLv2',
    'NCSA',
    'neovim',
    'nfsidmap',
    'NoCopyright',
    'OASIS',
    'OFL',
    'OFL-1.1',
    'OPEN DATA LICENSE',
    'OpenLDAP',
    'OpenMPI',
    'OSGPL',
    'perl',
    'PerlArtistic',
    'PerlArtistic2',
    'PHP',
    'PHP-3.01',
    'pil',
    'PostgreSQL',
    'PSF',
    'Public',
    'Public Domain',
    'Python',
    'Qhull',
    'QPL',
    'QPL-1.0',
    'qwt',
    'Ruby',
    'scite',
    'scowl',
    'Sendmail',
    'Sendmail open source license',
    'SGI',
    'SIL',
    'SIL Open Font License',
    'SIL Open Font License 1.1 and Bitstream Vera License',
    'SIL Open Font License, Version 1.0',
    'SIL OPEN FONT LICENSE Version 1.1',
    'sip',
    'Sleepycat',
    'tcl',
    'TekHVC',
    'TRADEMARKS',
    'Tumbolia',
    'UBDL',
    'Ubuntu Font License 1.0',
    'UCD',
    'UFL-1.0',
    'Unicode-DFS',
    'University of California and Stanford University License',
    'University of Illinois/NCSA Open Source License',
    'Unlicense',
    'usermin',
    'vim',
    'voidspace',
    'W3C',
    'w3m',
    'webmin',
    'WTF',
    'WTFPL',
    'wxWindows',
    'X11',
    'X11-DEC',
    'XFREE86',
    'Xiph',
    'zlib',
    'zlib/libpng',
    'ZPL',
]]

# Licenses with shared source code but with ethical restrictions -
# technically not open source but deserve mention
# see https://ethicalsource.dev/
ETHICAL_LICENSES = [clean_license_name(license) for license in [
    'JSON', # "shall be used for Good, not Evil"
    'ACSL',
    'Anti-966',
    'Atmosphere',
    'CNPL',
    'Hippocratic',
    'Hippocratic 2.1',
    'NoHarm',
    'NoHarm-draft',
    'NPL',
    'PPL',
]]

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

        # packages with a known "ethical" license
        self.ethical_packages = set()

    def visit_db(self, db):
        pkgs = db.packages
        self.num_pkgs += len(db.packages)

        free_pkgs = []

        for pkg in pkgs:
            licenses = []

            # get a list of all licenses on the box
            for license in pkg.licenses:
                clean_license = clean_license_name(license)
                licenses.append(clean_license)

                if clean_license not in self.by_license:
                    self.by_license[clean_license] = [pkg]
                else:
                    self.by_license[clean_license].append(pkg)

                if clean_license not in self.license_names:
                    self.license_names[clean_license] = {}
                if license not in self.license_names[clean_license]:
                    self.license_names[clean_license][license] = 0
                self.license_names[clean_license][license] += 1

            free_licenses = list(filter(lambda x: x in FREE_LICENSES, licenses))
            amb_licenses = list(filter(lambda x: x in AMBIGUOUS_LICENSES, licenses))
            ethical_licenses = list(filter(lambda x: x in ETHICAL_LICENSES, licenses))

            if free_licenses and len(free_licenses) == len(licenses):
                free_pkgs.append(pkg)
            elif len(amb_licenses) > 0 or not licenses:
                self.unknown_packages.add(pkg)
            else:
                self.nonfree_packages.add(pkg)

            if len(ethical_licenses) > 0:
                self.ethical_packages.add(pkg)


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
