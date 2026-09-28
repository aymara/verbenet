#!/usr/bin/env python3
"""Upload dist/hf/ to a Hugging Face dataset repository and tag it with the version.

Usage: HF_TOKEN=... uv run --group release scripts/publish_hf.py REPO_ID [--folder dist/hf]

Run scripts/release_assets.py first. The repository is created if it does not exist.
"""
import argparse
import sys
from pathlib import Path

from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import verbenet  # noqa: E402

ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("repo_id", help="e.g. aymaralima/verbenet")
ap.add_argument("--folder", type=Path, default=ROOT / "dist" / "hf")
args = ap.parse_args()

version = verbenet.__version__
api = HfApi()  # reads the token from HF_TOKEN or the local login
api.create_repo(args.repo_id, repo_type="dataset", exist_ok=True)
api.upload_folder(repo_id=args.repo_id, repo_type="dataset", folder_path=args.folder,
                  commit_message=f"Verb∋Net {version}", delete_patterns=["*.jsonl", "xml/*"])
api.create_tag(args.repo_id, repo_type="dataset", tag=version, exist_ok=True)
print(f"Published Verb∋Net {version} to https://huggingface.co/datasets/{args.repo_id}")
