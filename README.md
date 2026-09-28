Verb∋Net
========

**Verb∋Net** is a lexicon of French verbs organised in the same way as the English
[VerbNet](https://verbs.colorado.edu/verbnet/). Verbs are grouped into classes that share thematic roles
(with selectional restrictions) and syntactic frames, and each frame has an example and a semantic formula.

**Website: https://aymara.github.io/verbenet/**. Browse the classes, look up a verb and read the format
documentation.

*Verb∋Net est une version française de VerbNet : 229 classes de verbes, 2 827 verbes distincts et 525 schémas
syntaxiques, avec rôles thématiques, exemples et sémantique.*

## Getting the data

Each release is available in the following forms, which all contain the same data:

- **GitHub Releases**: [latest release](https://github.com/aymara/verbenet/releases/latest). It includes
  `verbenet-data-X.Y.Z.zip` (XML files, schema, JSON Lines tables) and the Python package.
- **Zenodo**: every release is archived with a DOI.
- **Python**: `pip install verbenet` (or `uv add verbenet`):
  ```python
  import verbenet
  classes = verbenet.load()               # nested dicts, one per top-level class
  frames = list(verbenet.frame_rows())    # one flat dict per frame, with inherited roles and members resolved
  verbenet.DATA_DIR                       # the raw XML files
  ```
- **Hugging Face**: [aymaralima/verbenet](https://huggingface.co/datasets/aymaralima/verbenet), `load_dataset("aymaralima/verbenet", "frames")` (or `"members"`).

## Contents

| Path | Description |
| --- | --- |
| `verbenet/<name>-<number>.xml` | One file per class (`VNCLASS`), in VerbNet's XML format. **This is the reference data.** |
| `verbenet/VERBENET.xml` | Aggregate that includes every class file with XInclude and carries the version number |
| `verbenet/VERBENET.rnc` | RELAX NG (compact) schema for a class file or for the aggregate |
| `src/verbenet/` | Python loader, shipped with the data in the `verbenet` package |
| `scripts/` | Validation, website, release assets and Hugging Face publication |
| `site/`, `hf/` | Website sources, Hugging Face dataset card template |

The current data has 229 classes, 97 subclasses, 525 frames and 4,177 verb–class pairs (2,827 distinct verbs).

```sh
# all the classes of a verb
xmllint --xinclude --xpath '//MEMBER[@name="manger"]/ancestor::*[@ID][1]/@ID' verbenet/VERBENET.xml
```

## How it was built

Verb∋Net was built at CEA LIST and Université Paris Diderot, in the ANR ASFALDA project. The method keeps
VerbNet's hierarchy and semantics, and takes the French verbs from two French lexicons: *Les Verbes Français* (LVF)
and the *Lexique-Grammaire* (LG). Each VerbNet class was linked to LVF classes and LG tables, which are kept in the
`lvf` and `ladl` attributes. Translations of the English members were kept only if they belong to those classes or
tables. Frames were then adapted to French by hand.
See the [website](https://aymara.github.io/verbenet/#how-it-was-built) and the paper below for details.

## This revision

This version of the [original release](https://github.com/aymara/verbenet/tree/cdd9e89) was prepared by
Guy Lapalme and Marie-Claude L'Homme while studying the use of Verb∋Net for text generation. It:

- adds `VERBENET.xml`, which includes all the XML files, so that XPath queries can run over the whole lexicon;
- adds a RELAX NG schema to validate the XML files;
- fixes typos in some examples and member verbs;
- makes sure each `MEMBER` element contains exactly one verb;
- corrects some frames and roles so that they match their examples.

Contact: [Guy Lapalme](mailto:lapalme@iro.umontreal.ca)

## Versioning

Verb∋Net uses [semantic versioning](https://semver.org/), applied to data:

| Bump | When | Examples |
| --- | --- | --- |
| **MAJOR** | Code that reads the data may break | Schema changes (elements or attributes renamed or removed, content model changed); class IDs renamed or removed; file layout changed |
| **MINOR** | The inventory changes, but the format still parses the same way | New classes, subclasses, frames or members; removed members or frames; new allowed values in the schema |
| **PATCH** | Corrections that don't change the inventory | Typos in examples, a role fixed to match its example, a wrong preposition |

The version is stored in `pyproject.toml`, `CITATION.cff` and the `version` attribute of `VERBENET.xml`.
Changes are listed in [CHANGELOG.md](CHANGELOG.md).

## Contributing and releasing

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv run scripts/validate.py             # schema, IDs, one verb per MEMBER, aggregate, version consistency
uv run scripts/build_site.py           # website into _site/
python3 -m http.server -d _site 8000   # preview it at http://localhost:8000
```

When editing data, add a line under **Unreleased** in `CHANGELOG.md`. When adding or renaming a class file, update
`VERBENET.xml` as well.

To release, on an up-to-date `master` with a clean working tree:

```sh
uv run scripts/validate.py
uv run bumpver update --minor     # or --patch / --major; --dry shows the diff first
git push --follow-tags
```

bumpver updates the version everywhere, turns the **Unreleased** section of the changelog into the new version,
commits and tags (e.g. `1.1.0`). Pushing the tag runs `.github/workflows/release.yml`, which validates and builds
everything, then creates the GitHub Release (Zenodo archives it) and publishes to PyPI and Hugging Face. Pushing to
`master` also redeploys the website (`.github/workflows/pages.yml`).

## Citing

Quentin Pradet, Laurence Danlos and Gaël de Chalendar. 2014.
[Adapting VerbNet to French using existing resources](https://aclanthology.org/L14-1204/).
In *Proceedings of the Ninth International Conference on Language Resources and Evaluation (LREC'14)*,
pages 1122–1126, Reykjavik, Iceland. ELRA.

```bibtex
@inproceedings{pradet-etal-2014-adapting,
    title = "Adapting {V}erb{N}et to {F}rench using existing resources",
    author = {Pradet, Quentin and Danlos, Laurence and de Chalendar, Ga{\"e}l},
    booktitle = "Proceedings of the Ninth International Conference on Language Resources and Evaluation ({LREC}'14)",
    month = may,
    year = "2014",
    address = "Reykjavik, Iceland",
    publisher = "European Language Resources Association (ELRA)",
    pages = "1122--1126"
}
```

To cite a specific version of the data, use its Zenodo DOI (see `CITATION.cff`, or *Cite this repository* on GitHub).

## License

Like the original Verb∋Net release, this version is distributed under the
[Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/)
(see [LICENSE](LICENSE)).
