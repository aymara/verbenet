#!/usr/bin/env python3
"""Check the Verb∋Net data before committing or releasing.

Usage: uv run scripts/validate.py

- every class file is valid against VERBENET.rnc;
- each class ID matches its file name, and each MEMBER holds a single verb;
- VERBENET.xml includes exactly the class files (non-ASCII names percent-encoded) and is valid;
- the version is the same in pyproject.toml, CITATION.cff and VERBENET.xml.
"""
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import quote

import rnc2rng
from lxml import etree

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "verbenet"

errors = []
schema = etree.RelaxNG(etree.fromstring(rnc2rng.dumps(rnc2rng.load(str(DATA / "VERBENET.rnc"))).encode()))

files = sorted(f for f in DATA.glob("*.xml") if f.name != "VERBENET.xml")
for f in files:
    doc = etree.parse(str(f))
    if not schema.validate(doc):
        errors.append(f"{f.name}: {schema.error_log.last_error}")
    if doc.getroot().get("ID") != f.stem:
        errors.append(f"{f.name}: ID {doc.getroot().get('ID')!r} does not match the file name")
    for m in doc.iter("MEMBER"):
        if re.search(r"[,;/]", m.get("name")):
            errors.append(f"{f.name}: MEMBER {m.get('name')!r} holds several verbs")

aggregate = etree.parse(str(DATA / "VERBENET.xml"))
hrefs = [i.get("href") for i in aggregate.iter("{http://www.w3.org/2001/XInclude}include")]
expected = [quote(f.name) for f in files]
for h in sorted(set(expected) - set(hrefs)):
    errors.append(f"VERBENET.xml: missing <xi:include href=\"{h}\">")
for h in sorted(set(hrefs) - set(expected)):
    errors.append(f"VERBENET.xml: includes {h}, which is not a class file")
if set(hrefs) == set(expected) and hrefs != expected:
    errors.append("VERBENET.xml: includes are not in file-name order")
version = aggregate.getroot().get("version")
try:
    aggregate.xinclude()
except etree.XIncludeError as e:
    errors.append(f"VERBENET.xml: {e}")
else:
    if not schema.validate(aggregate):
        errors.append(f"VERBENET.xml (expanded): {schema.error_log.last_error}")

versions = {
    "pyproject.toml": tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"],
    "CITATION.cff": re.search(r"^version: (\S+)$", (ROOT / "CITATION.cff").read_text(encoding="utf-8"), re.M).group(1),
    "VERBENET.xml": version,
}
if len(set(versions.values())) != 1:
    errors.append(f"version mismatch: {versions}")

for e in errors:
    print(e, file=sys.stderr)
print(f"{len(files)} class files, version {versions['pyproject.toml']}: "
      + ("OK" if not errors else f"{len(errors)} error(s)"))
sys.exit(1 if errors else 0)
