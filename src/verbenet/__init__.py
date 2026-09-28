"""Verb∋Net, a VerbNet-style lexicon of French verbs.

    import verbenet

    for cls in verbenet.load():            # top-level classes, sorted by class number
        for sub in verbenet.walk(cls):     # the class and all its subclasses
            print(sub["id"], sub["members"])

    rows = verbenet.frame_rows()           # one flat dict per frame, roles and members resolved

The raw XML files and the RELAX NG schema are in ``verbenet.DATA_DIR``.
"""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

__all__ = ["DATA_DIR", "__version__", "load", "walk", "frame_rows", "member_rows"]

_here = Path(__file__).resolve().parent
DATA_DIR = _here / "data"
if not DATA_DIR.is_dir():  # source checkout or editable install
    DATA_DIR = _here.parent.parent / "verbenet"

__version__ = re.search(r'<VERBENET version="([^"]+)"',
                        (DATA_DIR / "VERBENET.xml").read_text(encoding="utf-8")).group(1)


def class_sort_key(cid):
    """Sort key ordering class IDs by VerbNet number: 9.1 < 9.10 < 10.1."""
    name, number = re.match(r"^(.*?)-(\d.*)$", cid).groups()
    return [int(n) if n.isdigit() else n for n in re.split(r"[.-]", number)] + [name]


def _restrictions(node):
    """Render a SELRESTR/SELRESTRS tree as e.g. [+organization | +animate]."""
    if node.tag == "SELRESTR":
        return node.get("Value") + node.get("type")
    op = " | " if node.get("logic") == "or" else " & "
    return "[" + op.join(_restrictions(c) for c in node) + "]"


def _syntax(syn):
    out = []
    for x in syn:
        prepositions = restriction = None
        if x.tag == "PREP":
            r = x.find("SELRESTRS/SELRESTR")
            if r is not None and r.get("type"):
                restriction = r.get("Value") + r.get("type")
            elif r is not None:
                prepositions = r.get("Value").split(";")
        out.append({
            "element": x.tag,
            "role": x.get("value"),
            "modifier": x.get("modifier"),
            "pronominal": x.get("pronominal") == "true",
            "restr": x.get("restr"),
            "introduced_by": x.get("introduced_by"),
            "emptysubjectrole": x.get("emptysubjectrole"),
            "prepositions": prepositions,
            "restriction": restriction,
        })
    return out


def _parse_class(el, top, parent, file):
    roles = []
    for r in el.find("THEMROLES"):
        restr = next(iter(r), None)
        roles.append({"type": r.get("type"),
                      "restrictions": _restrictions(restr) if restr is not None else None})
    frames = []
    for f in el.find("FRAMES"):
        d = f.find("DESCRIPTION")
        frames.append({
            "primary": d.get("primary"),
            "syntax_description": d.get("syntax"),
            "examples": [(x.text or "").strip() for x in f.find("EXAMPLES")],
            "syntax": _syntax(f.find("SYNTAX")),
            "semantics": (f.findtext("SEMANTICS") or "").strip(),
        })
    cid = el.get("ID")
    return {
        "id": cid, "top": top, "parent": parent, "file": file,
        "ladl": el.get("ladl"), "lvf": el.get("lvf"),
        "members": [m.get("name") for m in el.find("MEMBERS")],
        "roles": roles, "frames": frames,
        "subclasses": [_parse_class(s, top, cid, file) for s in el.findall("SUBCLASSES/VNSUBCLASS")],
    }


def load(data_dir=None):
    """Parse every class file. Returns the top-level classes as nested dicts, sorted by number."""
    classes = []
    for f in Path(data_dir or DATA_DIR).glob("*.xml"):
        if f.name == "VERBENET.xml":
            continue
        root = ET.parse(f).getroot()
        classes.append(_parse_class(root, root.get("ID"), None, f.name))
    classes.sort(key=lambda c: class_sort_key(c["id"]))
    return classes


def walk(cls):
    """Yield a class and all its subclasses, depth first."""
    yield cls
    for s in cls["subclasses"]:
        yield from walk(s)


def _resolved(classes):
    """Yield (class, roles, ladl, lvf) with roles and LG/LVF links inherited from ancestors.

    A subclass that restates a role replaces the parent's restrictions for that role."""
    def rec(c, roles, ladl, lvf):
        roles = dict(roles)
        roles.update((r["type"], r) for r in c["roles"])
        ladl, lvf = c["ladl"] or ladl, c["lvf"] or lvf
        yield c, list(roles.values()), ladl, lvf
        for s in c["subclasses"]:
            yield from rec(s, roles, ladl, lvf)
    for c in classes:
        yield from rec(c, {}, None, None)


def frame_rows(classes=None):
    """One flat dict per frame. ``members`` lists every verb the frame applies to, i.e. the members
    of the class that defines it and of all its subclasses; ``roles`` includes inherited roles."""
    for c, roles, ladl, lvf in _resolved(classes or load()):
        members = [m for s in walk(c) for m in s["members"]]
        for i, f in enumerate(c["frames"]):
            yield {"class_id": c["id"], "top_class": c["top"], "parent_class": c["parent"],
                   "frame_index": i, **f, "roles": roles, "members": members,
                   "lg_tables": ladl, "lvf_classes": lvf}


def member_rows(classes=None):
    """One flat dict per (verb, class) pair."""
    for c, roles, ladl, lvf in _resolved(classes or load()):
        for m in c["members"]:
            yield {"verb": m, "class_id": c["id"], "top_class": c["top"],
                   "parent_class": c["parent"], "lg_tables": ladl, "lvf_classes": lvf}
