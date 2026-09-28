#!/usr/bin/env python3
"""Build the data release assets into dist/ (Python standard library only).

Usage: python3 scripts/release_assets.py [--out dist] [--repo-id aymaralima/verbenet]

- dist/verbenet-data-X.Y.Z.zip: the XML files, the schema, the JSON Lines tables and the metadata files;
- dist/hf/: the Hugging Face dataset folder (dataset card, JSON Lines tables, XML files).

The Python package itself is built separately with `uv build`.
"""
import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # works without installing the package

import verbenet  # noqa: E402

META = ["README.md", "CHANGELOG.md", "CITATION.cff", "LICENSE"]


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def counts(classes):
    everything = [s for c in classes for s in verbenet.walk(c)]
    members = [m for s in everything for m in s["members"]]
    return {
        "n_classes": f"{len(classes):,}",
        "n_subclasses": f"{len(everything) - len(classes):,}",
        "n_frames": f"{sum(len(s['frames']) for s in everything):,}",
        "n_members": f"{len(members):,}",
        "n_verbs": f"{len(set(members)):,}",
    }


def build(out, repo_id):
    version = verbenet.__version__
    classes = verbenet.load()
    hf = out / "hf"
    if hf.exists():
        shutil.rmtree(hf)
    (hf / "xml").mkdir(parents=True)

    write_jsonl(hf / "frames.jsonl", verbenet.frame_rows(classes))
    write_jsonl(hf / "members.jsonl", verbenet.member_rows(classes))
    for f in verbenet.DATA_DIR.iterdir():
        shutil.copy(f, hf / "xml" / f.name)
    values = {"version": version, "repo_id": repo_id, **counts(classes)}
    card = (ROOT / "hf" / "dataset_card.md").read_text(encoding="utf-8")
    (hf / "README.md").write_text(re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], card), encoding="utf-8")

    archive = out / f"verbenet-data-{version}.zip"
    prefix = f"verbenet-data-{version}"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(verbenet.DATA_DIR.iterdir()):
            z.write(f, f"{prefix}/verbenet/{f.name}")
        for name in ("frames.jsonl", "members.jsonl"):
            z.write(hf / name, f"{prefix}/{name}")
        for name in META:
            z.write(ROOT / name, f"{prefix}/{name}")
    print(f"Built {archive} and {hf}/ for version {version}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=ROOT / "dist")
    ap.add_argument("--repo-id", default="aymaralima/verbenet", help="Hugging Face dataset id used in the card")
    args = ap.parse_args()
    args.out.mkdir(exist_ok=True)
    build(args.out, args.repo_id)
