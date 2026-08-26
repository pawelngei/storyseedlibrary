#!/usr/bin/env python3
"""Sync content translations with the po/ gettext files (Weblate pipeline).

For each section (art, seeds, authors, tags, pages, essays):
1. Scan content/ for English masters and regenerate po4a/{section}.cfg.
2. Run po4a: updates po/{section}/{section}.pot, msgmerges the per-language
   .po files, and (re)writes translated index.{lang}.md files for documents
   translated above the keep threshold. Existing files below the threshold
   are left untouched (--keep-translations).
3. Normalize the PO layout (msgcat --no-wrap): one line per string, so
   gettext and Weblate stop reflowing each other's line breaks.
4. Fix up aliases in translated files: each alias gets a /{lang}/ prefix
   (Hugo aliases are language-prefixed; the English master's aliases are not).
5. Authors only: drop the `social:` block from translated files - only the
   English master carries it; author-resolve.html falls back per-param.

Run this after editing English content and after merging a Weblate PR.
Translated index.{lang}.md files are GENERATED - do not hand-edit them;
translate via Weblate (or edit the po/{section}/{lang}.po files) instead.

Usage: python3 scripts/po_sync.py [--section art,seeds,...] [--pot-only]
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
PO_DIR = ROOT / "po"
CFG_DIR = ROOT / "po4a"

KEEP_THRESHOLD = 80  # % translated below which a translated md is not written

# Front-matter keys exposed to translators; everything else (tags, authors,
# aliases, social, dates...) is copied verbatim from the English master.
YFM_KEYS = "title,description,bio"

SECTION_GLOBS = {
    "art": ["art/*/*/index.en.md"],
    "seeds": ["seeds/*/index.en.md"],
    "authors": ["authors/*/_index.en.md"],
    "tags": ["tags/*/_index.en.md"],
    "essays": ["essays/*/index.en.md"],
    # 'pages' also owns the site root and section list pages
    "pages": ["pages/*/index.en.md", "_index.en.md", "*/_index.en.md"],
}
SECTIONS = list(SECTION_GLOBS)


def languages():
    langs = sorted(
        p.name.split(".")[1]
        for p in (ROOT / "config" / "_default").glob("languages.*.toml")
    )
    return [lang for lang in langs if lang != "en"]


def masters(section):
    files = set()
    for pattern in SECTION_GLOBS[section]:
        files.update(CONTENT.glob(pattern))
    return sorted(files)


def localized(master: Path, lang: str) -> Path:
    return master.with_name(master.name.replace(".en.md", f".{lang}.md"))


def write_cfg(section, langs):
    """(Re)generate po4a/{section}.cfg; report master list changes."""
    cfg_path = CFG_DIR / f"{section}.cfg"
    old_masters = set()
    if cfg_path.exists():
        for line in cfg_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("[type: text]"):
                old_masters.add(line.split()[2])

    lines = [
        f"[po4a_langs] {' '.join(langs)}",
        f"[po4a_paths] po/{section}/{section}.pot $lang:po/{section}/$lang.po",
        # NB: no neverwrap - it splits list items with blank lines (loose
        # lists render differently); default 76-col reflow is render-neutral.
        # --wrap-po no keeps PO strings on a single line - but it only
        # reaches the POT po4a writes itself; the per-language files come
        # from msgmerge, so unwrap_po() below finishes the job. Affects the
        # .po layout only, never the generated md.
        "[options] --option markdown "
        f'--option "yfm_keys={YFM_KEYS}" --option yfm_skip_array '
        f"--keep {KEEP_THRESHOLD} --porefs file --wrap-po no "
        "--master-charset UTF-8 --localized-charset UTF-8",
    ]
    new_masters = set()
    for master in masters(section):
        rel = master.relative_to(ROOT).as_posix()
        loc = rel.replace(".en.md", ".$lang.md")
        lines.append(f"[type: text] {rel} $lang:{loc}")
        new_masters.add(rel)

    cfg_path.parent.mkdir(exist_ok=True)
    cfg_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for added in sorted(new_masters - old_masters):
        if old_masters:
            print(f"  new master: {added}")
    for removed in sorted(old_masters - new_masters):
        print(f"  REMOVED master: {removed} (its PO entries become obsolete)")
    return cfg_path


# POT header metadata; passed on the command line, not in the cfg [options]
# string, whose parser mishandles quoted and empty arguments. Per-language
# .po headers are Weblate's job.
POT_HEADER_OPTS = [
    "--package-name",
    "story-seed-library",
    "--package-version",
    "1.0",
    "--copyright-holder",
    "Story Seed Library contributors (CC BY-SA 4.0)",
    "--msgid-bugs-address",
    "https://codeberg.org/alxd/storyseedlibrary/issues",
]


def run_po4a(cfg_path, pot_only):
    cmd = ["po4a", "--force", "--keep-translations", *POT_HEADER_OPTS]
    if pot_only:
        cmd.append("--no-translations")
    cmd.append(str(cfg_path.relative_to(ROOT)))
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    interesting = [
        line
        for line in (result.stdout + result.stderr).splitlines()
        if "discard" in line.lower() or "%" in line or "error" in line.lower()
    ]
    for line in interesting:
        print(f"  {line}")
    if result.returncode != 0:
        print(
            f"  po4a FAILED (exit {result.returncode}) for {cfg_path.name}",
            file=sys.stderr,
        )
        tail = (result.stderr or result.stdout).splitlines()[-15:]
        print("  " + "\n  ".join(tail), file=sys.stderr)
    return result.returncode == 0


def unwrap_po(section):
    """Rewrite po/{section}/*.po(t) with every string on one physical line.

    gettext and Weblate wrap long strings at different break points inside
    unbreakable words (URLs mostly: gettext breaks after `.`, Weblate after
    `-`), so each side reflowed what the other had written and every file
    showed up in the diff on every sync, translations unchanged.

    `msgcat --no-wrap` is idempotent and covers msgid/msgstr, the `#|`
    previous-msgid comments and obsolete `#~` entries, so the files stay
    byte-stable whoever writes them last. Weblate needs the matching
    setting: "Customize gettext output" add-on, wrap length 65535.
    """
    changed = 0
    for path in sorted((PO_DIR / section).glob("*.po*")):
        tmp = path.with_name(path.name + ".unwrap")
        result = subprocess.run(
            ["msgcat", "--no-wrap", "-o", str(tmp), str(path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            tmp.unlink(missing_ok=True)
            print(f"  msgcat FAILED for {path.name}: {result.stderr.strip()}")
            continue
        if tmp.read_bytes() != path.read_bytes():
            tmp.replace(path)
            changed += 1
        else:
            tmp.unlink()
    if changed:
        print(f"  unwrapped {changed} po files")


ALIAS_ITEM_RE = re.compile(r"""^(\s*-\s*)(["']?)(/[^"']*?)(\2\s*)$""")


def fix_aliases(path: Path, lang: str) -> bool:
    """Prefix alias targets with /{lang}/ in a translated file's front matter.

    Line-based on purpose: no YAML round-trip, so quoting/formatting of the
    rest of the front matter is never disturbed.
    """
    lines = path.read_text(encoding="utf-8").split("\n")
    if not lines or lines[0].strip() != "---":
        return False
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return False

    changed = False
    in_aliases = False
    for i in range(1, end):
        line = lines[i]
        if re.match(r"^aliases\s*:", line):
            in_aliases = True
            continue
        if in_aliases:
            m = ALIAS_ITEM_RE.match(line)
            if m:
                target = m.group(3)
                if not target.startswith(f"/{lang}/"):
                    lines[i] = f"{m.group(1)}{m.group(2)}/{lang}{target}{m.group(4)}"
                    changed = True
            elif line and not line[0].isspace():
                in_aliases = False
    if changed:
        path.write_text("\n".join(lines), encoding="utf-8")
    return changed


def strip_social(path: Path) -> bool:
    """Remove the front-matter `social:` block from a translated author file.

    Only the English master needs `social` - author-resolve.html falls back to
    it for any param the translation leaves unset. Line-based like
    fix_aliases: the block is the `social:` line plus every following line
    indented deeper than it.
    """
    lines = path.read_text(encoding="utf-8").split("\n")
    if not lines or lines[0].strip() != "---":
        return False
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return False

    start = next(
        (i for i in range(1, end) if re.match(r"^(\s+)social\s*:\s*$", lines[i])), None
    )
    if start is None:
        return False
    indent = len(lines[start]) - len(lines[start].lstrip())
    stop = start + 1
    while stop < end:
        stripped = lines[stop].strip()
        cur = len(lines[stop]) - len(lines[stop].lstrip())
        if stripped and cur <= indent:
            break
        stop += 1
    new = lines[:start] + lines[stop:]

    # If `social` was the only child of `params:`, an empty `params:` remains,
    # which Hugo rejects (nil is not a map) - drop it too.
    for i, line in enumerate(new):
        if re.match(r"^(\s*)params\s*:\s*$", line):
            p_indent = len(line) - len(line.lstrip())
            nxt = next((l for l in new[i + 1 :] if l.strip()), "---")
            if nxt.strip() == "---" or len(nxt) - len(nxt.lstrip()) <= p_indent:
                del new[i]
            break

    path.write_text("\n".join(new), encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--section", help="comma-separated subset of: " + ",".join(SECTIONS)
    )
    parser.add_argument(
        "--pot-only",
        action="store_true",
        help="update POT/PO files, don't write translated md",
    )
    args = parser.parse_args()

    sections = args.section.split(",") if args.section else SECTIONS
    for section in sections:
        if section not in SECTIONS:
            sys.exit(f"unknown section {section!r} (choose from {SECTIONS})")

    langs = languages()
    print(f"languages: {' '.join(langs)}")
    ok = True
    for section in sections:
        print(f"\n=== {section} ({len(masters(section))} masters)")
        (PO_DIR / section).mkdir(parents=True, exist_ok=True)
        cfg_path = write_cfg(section, langs)
        ok &= run_po4a(cfg_path, args.pot_only)
        unwrap_po(section)

        if not args.pot_only:
            fixed = stripped = 0
            for master in masters(section):
                for lang in langs:
                    loc = localized(master, lang)
                    if not loc.exists():
                        continue
                    if fix_aliases(loc, lang):
                        fixed += 1
                    if section == "authors" and strip_social(loc):
                        stripped += 1
            if fixed:
                print(f"  aliases fixed in {fixed} files")
            if stripped:
                print(f"  social blocks stripped from {stripped} files")

    print("\n=== changed files (git):")
    subprocess.run(
        ["git", "status", "--short", "content/", "po/", "po4a/"], cwd=ROOT, check=False
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
