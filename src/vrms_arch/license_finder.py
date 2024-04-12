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
    "CC",
    "CCPL",
    "Creative Commons",
]]

FREE_LICENSES = [clean_license_name(license) for license in [
    'AFL-1.1',
    'AFL-1.2',
    'AFL-2.0',
    'AFL-2.1',
    'AFL-3.0',
    'AGPL',
    'AGPL3',
    'AGPL-3.0-only',
    'AGPL-3.0-or-later',
    'Apache',
    'Apache-1.0',
    'Apache-1.1',
    'Apache-2.0',
    'Apache2',
    'Apache 2.0',
    'Apache 2.0 with LLVM Exception',
    'Apache License (2.0)',
    'APL-1.0',
    'APSL-1.0',
    'APSL-1.1',
    'APSL-1.2',
    'APSL-2.0',
    'Arphic Public License',
    'Artistic',
    'Artistic-1.0',
    'Artistic-1.0-cl8',
    'Artistic-1.0-Perl',
    'Artistic-2.0',
    'Artistic 2.0',
    'Beerware',
    'bitstream-vera',
    'BitTorrent-1.1',
    'BlueOak-1.0.0',
    'Boost',
    '0BSD',
    'BSD',
    'BSD-1-Clause',
    'BSD2',
    'BSD-2-Clause',
    'BSD-2-Clause-Patent',
    'BSD3',
    'BSD-3-Clause',
    'BSD-3-Clause-Clear',
    'BSD-3-Clause-LBNL',
    'BSD-4-Clause',
    'BSD License',
    'BSD-like',
    'BSDL',
    'BSD-style',
    'BSL',
    'BSL-1.0',
    'bzip2',
    'CAL-1.0',
    'CAL-1.0-Combined-Work-Exception',
    'CC0',
    'CC0-1.0',
    'CC-BY',
    'CC-BY-2.5',
    'CC-BY-3.0',
    'CC-BY-4.0',
    'CC-BY-SA',
    'CC-BY-SA-2.5',
    'CC-BY-SA-3.0',
    'CC-BY-SA-4.0',
    'CCPL:by',
    'CCPL:by-4.0'
    'CCPL:by-sa',
    'CCPL:cc-by',
    'CCPL:cc-by-sa',
    'CDDL',
    'CDDL-1.0',
    'CeCILL',
    'CECILL-2.0',
    'CECILL-2.1',
    'CECILL-B',
    'CECILL-C',
    'CERN-OHL-P-2.0',
    'CERN-OHL-S-2.0',
    'CERN-OHL-W-2.0',
    'ClArtistic',
    'CNRI-Python',
    'Condor-1.1',
    'CPAL-1.0',
    'CPL',
    'CPL-1.0',
    'Creative Commons, Attribution 3.0 Unported',
    'CUA-OPL-1.0',
    'custom:free',
    'dumb',
    'ECL-1.0',
    'ECL-2.0',
    'EDL',
    'EDL-1.0',
    'EFL-1.0',
    'EFL-2.0',
    'Entessa',
    'EPL',
    'EPL-1.0',
    'EPL-1.1',
    'EPL-2.0',
    'etpan',
    'EUDatagrid',
    'EUPL-1.1',
    'EUPL-1.2',
    'ex',
    'Expat',
    'Fair',
    'FDL',
    'FDL1.2',
    'FDL1.3',
    'FFSL',
    'FIPL',
    'font embedding exception',
    'Frameworx-1.0',
    'Free Public License 1.0.0',
    'FSFAP',
    'FTL',
    'GD',
    'GFDL',
    'GFDL-1.1-only',
    'GFDL-1.1-or-later',
    'GFDL-1.1-no-invariants-or-later',
    'GFDL-1.2-only',
    'GFDL-1.2-or-later',
    'GFDL-1.2-no-invariants-only',
    'GFDL-1.3',
    'GFDL-1.3-only',
    'GFDL-1.3-or-later',
    'GFL',
    'gnuplot',
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
    'GPL-3.0-with-GCC-exception',
    'GPL/BSD',
    'GPL+FE',
    'GPLv2+',
    'GPLv2',
    'GPLv3',
    'HPND',
    'IBM Public Licence',
    'icu',
    'IJG',
    'ImageMagick',
    'iMatix',
    'Imlib2',
    'Info-ZIP',
    'INN',
    'Intel',
    'IPA',
    'IPL-1.0',
    'ISC',
    'isc-dhcp',
    'Jam',
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
    'LGPL2.1 with linking exception',
    'LGPL3',
    'LGPLv3+',
    'LGPL-3.0',
    'LGPL-3.0-only',
    'LGPL-3.0-or-later',
    'LGPL-3.0+ with WxWindows-exception-3.1',
    'LGPL-exception',
    'libpng',
    'libtiff',
    'libxcomposite',
    'LiLiQ-P-1.1',
    'LiLiQ-R-1.1',
    'LiLiQ-Rplus-1.1',
    'LLGPL',
    'LPL-1.0',
    'LPL-1.02',
    'LPPL',
    'LPPL-1.2',
    'LPPL-1.3a',
    'LPPL-1.3c',
    'lsof',
    'MirOS',
    'MIT',
    'MIT-0',
    'MIT-Modern-Variant',
    'MIT-style',
    'MIT/X',
    'MITX11',
    'Modified BSD',
    'Motosoto',
    'MPL',
    'MPL-1.0',
    'MPL-1.1',
    'MPL2',
    'MPLv2',
    'MPL-2.0',
    'MPL-2.0-no-copyleft-exception',
    'MS-PL',
    'MS-RL',
    'MulanPSL-2.0',
    'Multics',
    'NASA-1.3',
    'Naumen',
    'NCSA',
    'NCSAOSL',
    'neovim',
    'nfsidmap',
    'NGPL',
    'NoCopyright',
    'Nokia',
    'NOSL',
    'NPL-1.0',
    'NPL-1.1',
    'NPOSL-3.0',
    'NTP',
    'NYSL',
    'OASIS',
    'OCLC-2.0',
    'ODbL-1.0',
    'OFL',
    'OFL-1.0',
    'OFL-1.1',
    'OFL-1.1-no-RFN',
    'OFL-1.1-RFN',
    'OGTSL',
    'OLDAP-2.3',
    'OLDAP-2.7',
    'OLDAP-2.8',
    'OLFL-1.3',
    'OPEN DATA LICENSE',
    'OpenLDAP',
    'OpenMPI',
    'OpenSSL',
    'OpenSSL Linking Exception',
    'OSET-PL-2.1',
    'OSL-1.0',
    'OSL-1.1',
    'OSL-2.0',
    'OSL-2.1',
    'OSL-3.0',
    'OSGPL',
    'perl',
    'PerlArtistic',
    'PerlArtistic2',
    'PHP',
    'PHP-3.0',
    'PHP-3.01',
    'pil',
    'PostgreSQL',
    'PSF',
    'Public',
    'public-domain',
    'Python',
    'Python-2.0',
    'Qhull',
    'QPL',
    'QPL-1.0',
    'qwt',
    'RPL-1.1',
    'RPL-1.5',
    'RPSL-1.0',
    'RSCPL',
    'Ruby',
    'scite',
    'scowl',
    'sdbus-c++ LGPL Exception 1.0',
    'Sendmail',
    'Sendmail open source license',
    'SGI',
    'SGI-B-2.0',
    'SIL',
    'SIL Open Font License',
    'SIL Open Font License 1.1 and Bitstream Vera License',
    'SIL Open Font License, Version 1.0',
    'SIL OPEN FONT LICENSE Version 1.1',
    'SimPL-2.0',
    'sip',
    'SISSL',
    'Sleepycat',
    'SMLNJ',
    'SPL-1.0',
    'tcl',
    'TekHVC',
    'TRADEMARKS',
    'Tumbolia',
    'UBDL',
    'Ubuntu Font License 1.0',
    'UCD',
    'UCL-1.0',
    'UFL-1.0',
    'Unicode-3.0',
    'Unicode-DFS',
    'Unicode-DFS-2016',
    'University of California and Stanford University License',
    'University of Illinois/NCSA Open Source License',
    'Unlicense',
    'UPL-1.0',
    'usermin',
    'vim',
    'voidspace',
    'VSL-1.0',
    'W3C',
    'w3m',
    'Watcom-1.0',
    'webmin',
    'WTF',
    'WTFPL',
    'wxWindows',
    'X11',
    'X11-DEC',
    'XFREE86',
    'XFree86-1.1',
    'xinetd',
    'Xiph',
    'Xnet',
    'YPL-1.1',
    'Zend-2.0',
    'Zimbra-1.3',
    'Zero-Clause BSD',
    'zlib',
    'zlib/libpng',
    'ZPL',
    'ZPL-2.0',
    'ZPL-2.1',
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
            clean_licenses = []

            # get a list of all licenses on the box
            for license in pkg.licenses:
                if "AND" in license:
                    licenses += license.split(" AND ")
                else:
                    licenses.append(license)

            for license in licenses:
                clean_license = clean_license_name(license)
                clean_licenses.append(clean_license)

                if clean_license not in self.by_license:
                    self.by_license[clean_license] = [pkg]
                else:
                    self.by_license[clean_license].append(pkg)

                if clean_license not in self.license_names:
                    self.license_names[clean_license] = {}
                if license not in self.license_names[clean_license]:
                    self.license_names[clean_license][license] = 0
                self.license_names[clean_license][license] += 1

            free_licenses = list(filter(lambda x: x in FREE_LICENSES, clean_licenses))
            amb_licenses = list(filter(lambda x: x in AMBIGUOUS_LICENSES, clean_licenses))
            ethical_licenses = list(filter(lambda x: x in ETHICAL_LICENSES, clean_licenses))

            if free_licenses and len(free_licenses) == len(clean_licenses):
                free_pkgs.append(pkg)
            elif len(amb_licenses) > 0 or not clean_licenses:
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
