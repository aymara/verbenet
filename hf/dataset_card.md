---
license: cc-by-sa-4.0
language:
- fr
pretty_name: Verb∋Net
tags:
- verbnet
- lexicon
- verb-classes
- semantic-role-labeling
- linguistics
size_categories:
- 1K<n<10K
configs:
- config_name: frames
  data_files: frames.jsonl
  default: true
- config_name: members
  data_files: members.jsonl
---

# Verb∋Net {{version}}

Verb∋Net is a lexicon of French verbs organised in the same way as the English
[VerbNet](https://verbs.colorado.edu/verbnet/). Verbs are grouped into classes that share thematic roles (with
selectional restrictions) and syntactic frames, and each frame has an example and a semantic formula.

- **Website:** https://aymara.github.io/verbenet/ (browse classes and verbs, format documentation)
- **Source and issues:** https://github.com/aymara/verbenet
- **Paper:** [Adapting VerbNet to French using existing resources](https://aclanthology.org/L14-1204/) (LREC 2014)

This version has {{n_classes}} classes, {{n_subclasses}} subclasses, {{n_frames}} frames and {{n_members}}
verb–class pairs ({{n_verbs}} distinct verbs).

## Contents

The XML files in `xml/` are the reference data, identical to the GitHub release. The two JSON Lines tables below are
derived from them for convenience:

- **`frames`**: one row per frame. Inheritance is already resolved: `roles` includes roles inherited from parent
  classes (a subclass that restates a role replaces its restrictions), and `members` lists every verb the frame
  applies to, i.e. the members of the class that defines it and of all its subclasses.

  | Field | Description |
  | --- | --- |
  | `class_id`, `top_class`, `parent_class` | The (sub)class that defines the frame, its top-level class and its parent |
  | `frame_index` | Position of the frame in its class |
  | `primary`, `syntax_description` | The frame in constituent notation (`NP V NP PP`) and with roles (`Agent V Theme`) |
  | `examples` | French example sentence(s) |
  | `syntax` | Ordered constituents: `element` (NP, VERB, PREP, PSUBJ, VINF…), `role`, and attributes such as `modifier`, `pronominal`, `introduced_by`, `prepositions` |
  | `semantics` | Semantic formula, e.g. `approve(during(E), Agent, Theme)` |
  | `roles` | Thematic roles with their selectional restrictions |
  | `members` | Verbs the frame applies to |
  | `lg_tables`, `lvf_classes` | Linked Lexique-Grammaire tables and Les Verbes Français classes (inherited if not set) |

- **`members`**: one row per (verb, class) pair: `verb`, `class_id`, `top_class`, `parent_class`, `lg_tables`,
  `lvf_classes`.

```python
from datasets import load_dataset

frames = load_dataset("{{repo_id}}", "frames", split="train")
members = load_dataset("{{repo_id}}", "members", split="train")
```

The data is also available as a Python package: `pip install verbenet`.

## Citation

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

To cite the data itself, use the Zenodo DOI [10.5281/zenodo.23018909](https://doi.org/10.5281/zenodo.23018909), which always resolves to the latest version.

## License

[Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/).
