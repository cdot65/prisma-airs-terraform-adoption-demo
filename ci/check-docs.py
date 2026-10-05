#!/usr/bin/env python3
"""Check local Markdown destinations and the integrity of published live evidence."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
checked = 0
for path in [ROOT / 'README.md', *sorted((ROOT / 'docs').glob('*.md')), *sorted((ROOT / 'evidence').glob('*.md'))]:
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if target.startswith(('http://', 'https://', '#', 'mailto:')):
            continue
        destination = (path.parent / target.split('#')[0]).resolve()
        if not destination.is_relative_to(ROOT) or not destination.is_file():
            raise SystemExit(f'Broken local link in {path.relative_to(ROOT)}: {target}')
        checked += 1
receipt = json.loads((ROOT / 'evidence/receipt.json').read_text())
for name, expected in receipt['source_sha256'].items():
    if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
        raise SystemExit(f'Published source changed since validation: {name}')
for name, expected in receipt['evidence_sha256'].items():
    if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
        raise SystemExit(f'Published evidence digest mismatch: {name}')
print(f'{checked} local documentation links and recorded source/evidence hashes passed.')
