import re

def clean_license_name(license):
    license = license.lower()
    license = re.sub(r'(?:^custom:|[,\s_"/\(\)\:-])', '', license)
    license = re.sub('licence', 'license', license)
    return license
