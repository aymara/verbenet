#!/usr/bin/env python3
"""Generate the Verb∋Net website (published on GitHub Pages) from the XML class files.

Usage: python3 scripts/build_site.py [--out _site]

Hand-written pages live in site/pages/ as HTML fragments; {{name}} placeholders in
them are replaced by values computed from the data. Class and verb pages are fully
generated. Only the Python standard library is needed.
"""
import argparse
import collections
import html
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # works without installing the package

import verbenet  # noqa: E402
from verbenet import walk  # noqa: E402

SITE = ROOT / "site"
REPO = "https://github.com/aymara/verbenet"

esc = html.escape

NAV = [("index.html", "Home"), ("format.html", "Format"),
       ("classes.html", "Classes"), ("verbs.html", "Verbs")]


# --------------------------------------------------------------------------- data

def token(t):
    """Display (kind, label, role, note) for a syntax element from verbenet.load()."""
    tag, notes = t["element"], []
    if tag == "NP":
        label = "NP"
        if t["modifier"]:
            notes.append(t["modifier"])
    elif tag == "VERB":
        label = "se V" if t["pronominal"] else "V"
        if t["restr"]:
            notes.append(t["restr"])
    elif tag == "PREP":
        if t["restriction"]:
            label = "{" + t["restriction"] + "}"
        elif t["prepositions"]:
            label = " | ".join(p.replace("_", " ") for p in t["prepositions"])
        else:
            label = "PREP"
    elif tag in ("IL", "LUI"):
        label = tag.lower()
    else:
        label = tag
    if t["introduced_by"]:
        notes.insert(0, t["introduced_by"] + " …")
    if t["emptysubjectrole"]:
        notes.append("subject = " + t["emptysubjectrole"])
    return tag.lower(), label, t["role"], " · ".join(notes)


def fold(s):
    """Accent- and case-insensitive sort key."""
    return "".join(ch for ch in unicodedata.normalize("NFD", s.lower())
                   if not unicodedata.combining(ch))


# --------------------------------------------------------------------------- layout

def page(title, body, depth=0, active=None, description=""):
    up = "../" * depth
    nav = "".join(
        f'<a href="{up}{href}"{" aria-current=page" if href == active else ""}>{label}</a>'
        for href, label in NAV)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description or 'Verb∋Net, a VerbNet-style lexicon of French verbs')}">
<link rel="stylesheet" href="{up}style.css">
</head>
<body>
<header class="top">
  <div class="wrap">
    <a class="brand" href="{up}index.html">Verb<span>∋</span>Net</a>
    <nav>{nav}<a href="{REPO}">GitHub</a></nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="wrap">
  Verb∋Net <a href="{REPO}/releases/tag/{verbenet.__version__}">{verbenet.__version__}</a> is distributed under the
  <a href="https://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0</a> license.
  Source and issues on <a href="{REPO}">GitHub</a>.
</footer>
<script src="{up}filter.js"></script>
</body>
</html>
"""


def render_token(kind, label, role, note):
    inner = f"<b>{esc(label)}</b>"
    if role:
        inner += f"<i>{esc(role)}</i>"
    if note:
        inner += f"<small>{esc(note)}</small>"
    return f'<span class="tok {kind}">{inner}</span>'


def render_class(c, depth=0):
    h = "h2" if depth == 0 else "h3"
    out = [f'<section class="cls depth{min(depth, 3)}" id="{esc(c["id"])}">']
    if depth:
        out.append(f'<{h}><a href="#{esc(c["id"])}">{esc(c["id"])}</a></{h}>')
        if c["ladl"] or c["lvf"]:
            out.append(render_sources(c))
    if c["members"]:
        out.append(f'<h4>Members <span class="count">{len(c["members"])}</span></h4><ul class="chips">')
        out += [f'<li><a href="{"../verbs.html"}#{quote(m)}">{esc(m)}</a></li>' for m in c["members"]]
        out.append("</ul>")
    if c["roles"]:
        out.append('<h4>Thematic roles</h4><ul class="roles">')
        for role in c["roles"]:
            r = f' <code>{esc(role["restrictions"])}</code>' if role["restrictions"] else ""
            out.append(f"<li><span class=role>{esc(role['type'])}</span>{r}</li>")
        out.append("</ul>")
    if c["frames"]:
        out.append(f'<h4>Frames <span class="count">{len(c["frames"])}</span></h4>')
        for f in c["frames"]:
            ex = "".join(f"<blockquote lang=fr>{esc(x)}</blockquote>" for x in f["examples"])
            toks = "".join(render_token(*token(t)) for t in f["syntax"])
            out.append(f"""<div class="frame">
  <div class="frame-head"><code class="primary">{esc(f["primary"])}</code><span class="sdesc">{esc(f["syntax_description"])}</span></div>
  {ex}
  <div class="syntax">{toks}</div>
  <div class="sem"><code>{esc(f["semantics"])}</code></div>
</div>""")
    for s in c["subclasses"]:
        out.append(render_class(s, depth + 1))
    out.append("</section>")
    return "\n".join(out)


def render_sources(c):
    parts = []
    if c["ladl"]:
        parts.append(f'<span><abbr title="Lexique-Grammaire table(s)">LG</abbr> <code>{esc(c["ladl"])}</code></span>')
    if c["lvf"]:
        parts.append(f'<span><abbr title="Les Verbes Français class(es)">LVF</abbr> <code>{esc(c["lvf"])}</code></span>')
    return '<p class="sources">' + "".join(parts) + "</p>"


# --------------------------------------------------------------------------- pages

def class_page(c, prev, nxt):
    all_members = sum(len(s["members"]) for s in walk(c))
    all_frames = sum(len(s["frames"]) for s in walk(c))
    nsub = sum(1 for _ in walk(c)) - 1
    src = f'../data/{quote(c["file"])}'
    pager = '<nav class="pager">'
    pager += f'<a href="{quote(prev["id"])}.html">← {esc(prev["id"])}</a>' if prev else "<span></span>"
    pager += f'<a href="{quote(nxt["id"])}.html">{esc(nxt["id"])} →</a>' if nxt else "<span></span>"
    pager += "</nav>"
    toc = ""
    if c["subclasses"]:
        toc = '<nav class="subtoc"><span>Subclasses:</span> ' + " ".join(
            f'<a href="#{esc(s["id"])}">{esc(s["id"])}</a>' for s in walk(c) if s is not c) + "</nav>"
    body = f"""<p class="crumbs"><a href="../classes.html">Classes</a> /</p>
<h1 class="classid">{esc(c["id"])}</h1>
<div class="classmeta">
  {render_sources(c)}
  <p class="stats">{all_members} members · {all_frames} frames · {nsub} subclass{"es" if nsub != 1 else ""}
  · <a href="{src}">XML</a> · <a href="{REPO}/blob/master/verbenet/{quote(c["file"])}">view on GitHub</a></p>
</div>
{toc}
<p class="note">Members of a subclass also take the thematic roles and frames of the classes above it.</p>
{render_class(c)}
{pager}"""
    return page(f"{c['id']} · Verb∋Net", body, depth=1, active="classes.html",
                description=f"Verb∋Net class {c['id']}: {', '.join(c['members'][:8])}")


def classes_page(classes):
    rows = []
    for c in classes:
        members = [m for s in walk(c) for m in s["members"]]
        frames = sum(len(s["frames"]) for s in walk(c))
        name, number = re.match(r"^(.*?)-(\d.*)$", c["id"]).groups()
        sample = ", ".join(members[:6]) + (" …" if len(members) > 6 else "")
        search = fold(" ".join([c["id"]] + members))
        rows.append(f"""<tr data-search="{esc(search)}">
  <td class="num">{esc(number)}</td>
  <td><a href="classes/{quote(c["id"])}.html">{esc(name.replace("_", " "))}</a></td>
  <td class="n">{len(members)}</td><td class="n">{frames}</td>
  <td class="verbs" lang="fr">{esc(sample)}</td>
</tr>""")
    body = f"""<h1>Classes</h1>
<p class="lede">The {len(classes)} top-level classes of Verb∋Net, numbered as in VerbNet and Levin (1993).
Filter by class name or by verb.</p>
<input class="filter" type="search" placeholder="Filter: e.g. put, 45, manger…" data-target="#classtable tbody tr" aria-label="Filter classes">
<p class="filter-count" aria-live="polite"></p>
<div class="tablewrap"><table id="classtable">
<thead><tr><th>#</th><th>Class</th><th class="n">Verbs</th><th class="n">Frames</th><th>Members</th></tr></thead>
<tbody>
{"".join(rows)}
</tbody></table></div>"""
    return page("Classes · Verb∋Net", body, active="classes.html")


def verbs_page(classes):
    index = collections.defaultdict(list)
    for c in classes:
        for s in walk(c):
            for m in s["members"]:
                index[m].append(s)
    verbs = sorted(index, key=lambda v: (fold(v), v))
    groups = collections.OrderedDict()
    for v in verbs:
        groups.setdefault(fold(v)[:1].upper(), []).append(v)
    letters = " ".join(f'<a href="#letter-{k}">{k}</a>' for k in groups)
    parts = []
    for k, vs in groups.items():
        items = []
        for v in vs:
            links = " ".join(
                f'<a href="classes/{quote(s["top"])}.html#{esc(s["id"])}">{esc(s["id"])}</a>'
                for s in index[v])
            items.append(f'<li id="{esc(quote(v))}" data-search="{esc(fold(v))}"><span class="verb" lang="fr">{esc(v)}</span> {links}</li>')
        parts.append(f'<section class="letter" id="letter-{k}"><h2>{k}</h2><ul class="verblist">{"".join(items)}</ul></section>')
    body = f"""<h1>Verbs</h1>
<p class="lede">{len(verbs)} distinct verbs, with the classes they belong to. A verb listed in several classes has several senses or constructions.</p>
<input class="filter" type="search" placeholder="Filter verbs…" data-target=".verblist li" data-prefix aria-label="Filter verbs">
<p class="filter-count" aria-live="polite"></p>
<nav class="letters">{letters}</nav>
{"".join(parts)}"""
    return page("Verbs · Verb∋Net", body, active="verbs.html")


def stats(classes):
    everything = [s for c in classes for s in walk(c)]
    members = [m for s in everything for m in s["members"]]
    roles = collections.Counter(r["type"] for s in everything for r in s["roles"])
    restrs = collections.Counter()
    for s in everything:
        for r in s["roles"]:
            restrs.update(re.findall(r"[+-][a-z_]+", r["restrictions"] or ""))
    constituents = collections.Counter(t["element"].lower() for s in everything
                                       for f in s["frames"] for t in f["syntax"])
    preps = collections.Counter(token(t)[1] for s in everything for f in s["frames"]
                                for t in f["syntax"] if t["element"] == "PREP")

    def table(counter, head):
        rows = "".join(f"<tr><td><code>{esc(k)}</code></td><td class=n>{v}</td></tr>"
                       for k, v in counter.most_common())
        return f'<div class="tablewrap"><table class="compact"><thead><tr><th>{head}</th><th class=n>Uses</th></tr></thead><tbody>{rows}</tbody></table></div>'

    return {
        "version": verbenet.__version__,
        "n_classes": str(len(classes)),
        "n_subclasses": str(len(everything) - len(classes)),
        "n_frames": str(sum(len(s["frames"]) for s in everything)),
        "n_members": str(len(members)),
        "n_verbs": str(len(set(members))),
        "roles_table": table(roles, "Thematic role"),
        "restrictions_table": table(restrs, "Restriction"),
        "constituents_table": table(constituents, "Element"),
        "prepositions_table": table(preps, "Preposition(s)"),
    }


def fill(template, values):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], template)


def build(out):
    classes = verbenet.load()
    if out.exists():
        shutil.rmtree(out)
    (out / "classes").mkdir(parents=True)
    (out / "data").mkdir()

    values = stats(classes)
    for frag in sorted((SITE / "pages").glob("*.html")):
        text = frag.read_text(encoding="utf-8")
        title, _, body = text.partition("\n")  # first line: <!-- title: ... -->
        title = re.match(r"<!--\s*title:\s*(.*?)\s*-->", title).group(1)
        (out / frag.name).write_text(page(title, fill(body, values), active=frag.name), encoding="utf-8")

    (out / "classes.html").write_text(classes_page(classes), encoding="utf-8")
    (out / "verbs.html").write_text(verbs_page(classes), encoding="utf-8")
    for i, c in enumerate(classes):
        prev = classes[i - 1] if i else None
        nxt = classes[i + 1] if i + 1 < len(classes) else None
        (out / "classes" / f"{c['id']}.html").write_text(class_page(c, prev, nxt), encoding="utf-8")

    for f in SITE.glob("*.*"):
        shutil.copy(f, out / f.name)
    for f in verbenet.DATA_DIR.iterdir():
        shutil.copy(f, out / "data" / f.name)
    (out / ".nojekyll").touch()
    print(f"Built {len(classes)} class pages into {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=ROOT / "_site")
    build(ap.parse_args().out)
