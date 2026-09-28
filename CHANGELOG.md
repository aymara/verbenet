# Changelog

All notable changes to Verb∋Net are listed here. Versions follow the
[versioning policy](README.md#versioning). Add changes under **Unreleased** as you make them; the release
procedure renames that section to the new version.

## Unreleased

## 1.0.0

First versioned release. It has 229 classes, 97 subclasses, 525 frames and 4,177 verb–class pairs (2,827 distinct verbs).

Compared with the [original release](https://github.com/aymara/verbenet/tree/cdd9e89):

- `VERBENET.xml` includes every class file with XInclude, so XPath queries can run over the whole lexicon. It now
  has a `version` attribute.
- RELAX NG schema `VERBENET.rnc`, used to validate every file.
- Fixed typos in some examples and member verbs.
- Each `MEMBER` element contains exactly one verb.
- Corrected some frames and roles so that they match their examples.
- Documentation website, Python package (`pip install verbenet`) and flat JSON Lines exports.
