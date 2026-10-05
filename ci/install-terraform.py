#!/usr/bin/env python3
"""Install the exact reviewed Terraform archive after verifying its pinned digest."""
import hashlib
import io
from pathlib import Path
import urllib.request
import zipfile

VERSION = '1.16.4'
SHA256 = 'dc94af0eef1147718ad7c8daea792ed199e3e0492eec180d0adafa2a65a879df'
root = Path(__file__).resolve().parents[1]
archive = urllib.request.urlopen(
    f'https://releases.hashicorp.com/terraform/{VERSION}/terraform_{VERSION}_linux_amd64.zip',
    timeout=60).read()
if hashlib.sha256(archive).hexdigest() != SHA256:
    raise SystemExit('Terraform archive checksum mismatch')
(root / '.ci-bin').mkdir(exist_ok=True)
with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
    target = root / '.ci-bin/terraform'
    target.write_bytes(bundle.read('terraform'))
    target.chmod(0o700)
print('Installed checksum-verified Terraform ' + VERSION)
