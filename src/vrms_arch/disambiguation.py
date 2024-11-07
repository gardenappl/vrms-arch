import json
import os
import re
import sys

src_dir = os.path.join(os.path.dirname(__file__), "..")
src_dir = os.path.realpath(src_dir)

def clean_license_name(license: str):
    return re.sub(r"^(custom(:|=)|LicenseRef-)", "", license)

def filter_license_name(license: str):
    return re.sub(r"[_\-\s]", "", clean_license_name(license).lower())


class Package:
    def __init__(self, name, licenses, old_licenses=None):
        self.name = name
        self.licenses = licenses
        self.old_licenses = old_licenses or licenses


with open(os.path.join(src_dir, "ambiguous.json")) as f:
    ambiguous = json.load(f)
    ambiguous_free = list(map(filter_license_name, ambiguous["free"]))
    ambiguous_unknown = list(map(filter_license_name, ambiguous["unknown"]))

with open(os.path.join(src_dir, "vrms_licenses.tsv")) as f:
    aliases = dict()
    for line in f.read().splitlines():
        if line and line[0] != '#':
            names = line.split('\t')
            for alias in names[1:]:
                aliases[filter_license_name(alias)] = names[0]

with open(os.path.join(src_dir, "fixed_packages.tsv")) as f:
    fixed_packages = dict()
    for line in f.read().splitlines():
        if line and line[0] != '#':
            (name, fixed_license, old_license) = line.split('\t')
            old_license = old_license.split("  ")
            fixed_packages[name] = Package(name, [fixed_license], old_license)


class UnambiguousDb:
    def __init__(self, db, allow_amibiguous_free=False, print_unknown=False):
        self.packages = []
        self.unknown_packages = []

        for pkg in db.search(""):
            fixed_pkg = fixed_packages.get(pkg.name)
            if fixed_pkg:
                if fixed_pkg.old_licenses == pkg.licenses:
                    self.packages.append(fixed_pkg)
                    continue
                else:
                    print(pkg.name, "- Warning: outdated license fix", file=sys.stderr)

            licenses = list(map(clean_license_name, pkg.licenses))
            has_unknown = any(map(lambda l: filter_license_name(l) in ambiguous_unknown, licenses))
            if print_unknown and not has_unknown:
                continue
            elif not print_unknown and has_unknown:
                continue

            if allow_amibiguous_free:
                licenses = filter(lambda l: filter_license_name(l) not in ambiguous_free, licenses)
            licenses = list(map(lambda l: aliases.get(filter_license_name(l), l), licenses))

            new_pkg = Package(pkg.name, licenses, pkg.licenses)
            self.packages.append(new_pkg)
