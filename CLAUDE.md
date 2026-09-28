# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Verb∋Net, a French adaptation of the English VerbNet lexicon. It was built by Pradet, Danlos & de Chalendar (LREC 2014, https://aclanthology.org/L14-1204/) and revised by Guy Lapalme and Marie-Claude L'Homme. The XML files are the reference data. Everything else (Python loader, website, exports, release tooling) is derived from them. The lexical content (examples, member lemmas, schema comments) is in French. The documentation is in English. License: CC BY-SA 4.0.

## Layout

- `verbenet/<name>-<VerbNet number>.xml`: one file per verb class, with root `VNCLASS` and `ID` = file name without `.xml`. Subclass IDs extend it (`accept-77-1`).
- `verbenet/VERBENET.xml`: an aggregate that `xi:include`s every class file in file-name order and carries `version="X.Y.Z"`. **Update it when adding, removing or renaming a class file.** Percent-encode non-ASCII hrefs (`d%C3%A9valer-51.9.xml`), because libxml2 rejects raw ones.
- `verbenet/VERBENET.rnc`: the RELAX NG compact schema for a single class or for the aggregate.
- `src/verbenet/__init__.py`: the only parser of the data. `load()` returns nested class dicts, `walk()` iterates a class and its subclasses, and `frame_rows()`/`member_rows()` give flat rows with inheritance resolved (roles, `ladl`/`lvf`). `DATA_DIR` is `verbenet/data` in the wheel (hatchling force-includes the root `verbenet/` dir there) and falls back to the repo's `verbenet/`. `__version__` is read from `VERBENET.xml`.
- `scripts/build_site.py` + `site/`: the GitHub Pages site. `site/pages/*.html` are HTML fragments. Their first line is `<!-- title: ... -->`, and `{{name}}` placeholders are filled by `stats()`. Class pages, `classes.html` and `verbs.html` are generated.
- `scripts/release_assets.py` + `hf/dataset_card.md`: build `dist/verbenet-data-X.Y.Z.zip` and `dist/hf/` (JSON Lines tables, XML, filled dataset card). `scripts/publish_hf.py` uploads `dist/hf/` and tags it.
- The scripts put `src/` on `sys.path`, so `build_site.py` and `release_assets.py` also run with plain `python3`.

## Data model (see `VERBENET.rnc` and `site/pages/format.html`)

Each `VNCLASS`/`VNSUBCLASS` contains, in order: `MEMBERS`, `THEMROLES`, `FRAMES`, and an optional `SUBCLASSES`. Members of a subclass also take the roles and frames of the classes above it. A subclass that restates a role type overrides its restrictions. `ladl`/`lvf` link to Lexique-Grammaire tables and Les Verbes Français classes.

- `MEMBER name`: exactly one verb per element. Pronominal verbs put the clitic after the verb (`expliquer s'`).
- Roles, `SELRESTR` types and prepositions come from closed enumerations in the schema.
- `FRAME` = `DESCRIPTION` + `EXAMPLES` + `SYNTAX` + `SEMANTICS`. The schema constrains the order of the `SYNTAX` constituents, and every `NP` contains an empty `SYNRESTRS`. A frame's `SYNTAX` and roles should agree with its `DESCRIPTION` and its example. Many past corrections were of exactly that kind.

## Commands

```sh
uv run scripts/validate.py          # schema (via rnc2rng+lxml), IDs, one verb per MEMBER, aggregate, versions
uv run scripts/build_site.py        # site into _site/
uv run scripts/release_assets.py    # dist/ zip + Hugging Face folder
uv build                            # wheel + sdist
```

## Versioning and releases

Semantic versioning applied to data (policy table in README.md). MAJOR = schema, ID or layout changes. MINOR = inventory changes. PATCH = corrections. Data changes get a line under `## Unreleased` in `CHANGELOG.md`. Never edit version numbers by hand: `uv run bumpver update --patch|--minor|--major` updates `pyproject.toml`, `CITATION.cff` and `VERBENET.xml`, runs `scripts/bumpver_hook.py` (which renames the changelog section), then commits and tags `X.Y.Z` (no `v` prefix). Pushing the tag runs `.github/workflows/release.yml`: GitHub Release (archived by Zenodo), then PyPI (if the variable `PUBLISH_PYPI=true`) and Hugging Face (if the variable `HF_DATASET`, i.e. `aymaralima/verbenet`, and the secret `HF_TOKEN` are set). `.github/workflows/pages.yml` validates on every push and PR and deploys the site from `master`.
