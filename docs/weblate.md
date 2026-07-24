# Translations via Weblate (po4a pipeline)

Content translations are managed on [translate.codeberg.org](https://translate.codeberg.org)
using gettext PO files. The `index.{lang}.md` / `_index.{lang}.md` files in
`content/` are **generated** from those PO files - do not hand-edit them; any
manual change will be overwritten by the next sync. Translate in Weblate (or,
in a pinch, edit `po/{section}/{lang}.po` directly).

## Layout

```
po/{art,seeds,authors,tags,pages,essays}/
    {section}.pot              # English strings, extracted from content/
    {de,es,fr,it,pl,ti,ua}.po  # what Weblate edits
po4a/{section}.cfg             # generated per sync run, committed
scripts/po_sync.py             # recurring sync (see below)
```

Only `title`, `description` and `bio` front-matter values are translatable;
`tags`, `authors`, `aliases`, dates etc. are copied verbatim from the English
master. Author `social` links are the exception: only the English
`_index.en.md` carries them - the sync strips the block from translated author
files, and the bio box falls back to the English values per-param. The `ua` language code is nonstandard (Ukrainian); the Weblate
project maps it via a language alias, the repo keeps `ua` everywhere.

## Maintainer workflow

After editing English content, and after merging a Weblate PR:

```bash
python3 scripts/po_sync.py            # or --section art,tags,...
```

This regenerates `po4a/*.cfg`, updates the POT files, msgmerges the POs, and
rewrites every translated md that is ≥80% translated (files below the
threshold keep their current content - for old hand translations that could
not be imported, the hand-written file survives until Weblate catches up).
Aliases in generated files automatically get the `/{lang}/` prefix, and
translated author files get their `social:` block stripped. Review
`git status`, build with Hugo 0.145.0, commit `po/`, `po4a/` and `content/`
together.

Gotchas:

- Keep inline YAML lists in front matter on **one line**
  (`tags: ["a", "b"]`) - po4a's YAML parser rejects multiline flow lists.
- New English documents appear in the POT on the next sync; no other action
  needed. Deleted masters are dropped from the cfg and reported.
- A new tag needs `content/tags/{tag}/_index.en.md`
  (`scripts/gen_tag_masters.py` creates any that are missing).

## Adding a language

1. Add `config/_default/languages.{lang}.toml` + `menus.{lang}.toml`
   (config TOML stays manually translated - it is out of the pipeline's scope).
2. In each Weblate component, "Add new translation" - Weblate starts the PO
   from the component's POT template.
3. `po_sync.py` picks the language up automatically (it scans
   `config/_default/languages.*.toml`).


