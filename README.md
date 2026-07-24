# Story Seed Library

Welcome to the repository for the [Story Seed Library](https://storyseedlibrary.org/), a copyleft library of Solarpunk art and writing!

You can contribute to it on [Codeberg](https://codeberg.org/alxd/storyseedlibrary) and [Github](https://github.com/pawelngei/storyseedlibrary) - the merged commits will be [mirrored](https://codeberg.org/Recommendations/Mirror_to_Codeberg) between the platforms!

## Theme

This page is heavily based on a modified [blowfish](https://blowfish.page/) theme by Nuno Coração. The forked repository is configured as a submodule, available on [Codeberg]() and [Github](https://github.com/pawelngei/blowfish) (mirrored).

## Contributing

### Installation and development

After cloning the repository, please run:

```bash
git submodule init --recursive
git submodule update --recursive
```

To build the site, please install specifically Hugo [`0.145.0`](https://github.com/gohugoio/hugo/releases/tag/v0.145.0). After that, to preview your changes:

```bash
hugo serve -w
```

Sometimes related pages (like authors, tags) might not update automatically. You can force the update by running `hugo serve` in another console, or stopping the `-w` one, building statically, then restarting `-w`.

Then every time the theme updates, you'll need to run:

```bash
git submodule update --recursive
```

### Adding Authors

To add a new author:

1. Add a new catalog and file in `content/authors/{authorName}/_index.en.md`. The page `title` is the display name; add a `params.bio` and `params.social` (a list of `[{icon: url}]` maps) to configure Blowfish's `author-extra.html` bio box rendered on content pages.
2. Save the author's photo as `content/authors/{authorName}/portrait.jpg` (the small avatar shown in the bio box) and, separately, `content/authors/{authorName}/featured.jpg` (the cover image used elsewhere, e.g. author cards). The avatar can be 400x400px.
3. To translate the bio box, add `params.bio` (and optionally `title`) to `content/authors/{authorName}/_index.{lang}.md`; anything left unset falls back to the English version. `social` normally only needs to be set once, in English.
4. Now you can add the author in specific content articles. One article can have multiple authors, like:
  ```
  authors:
    - alxd
    - {authorName}
  ```

### Adding Art / Pages

To add new art by an existing / newly created author:

1. Create a new catalog in `content/{contentType}/{authorName}{urlSlug}/`, for example `content/art/the-lemonaut-community-center`.
2. Inside, create an `index.en.md` file with the content of the page / description and license of the art, listing the authors.
3. Save the high quality art as `featured.jpg` (not PNG or any other file) in the same catalog. It will be automatically scaled to different resolutions by hugo, and the original will be available once the user clicks the Full Resolution button.

### Adding Tags

To add a new tag:

1. Create a new file `content/tags/{tagName}/_index.en.md` which will determine the name and description of the tag, as well as how it will be displayed on cards.
2. Modify the content `index.en.md` by adding the `{tagName}` to specific lists, like:
  ```
  tags: ["illustration", "CC BY-SA 4.0", "my new tag"]
  ```
3. All spaces in the tag name are translated to `-` by Hugo.

### Translating

Translations are managed through [Weblate on Codeberg](https://translate.codeberg.org) - see [docs/weblate.md](docs/weblate.md) for the full pipeline documentation and the maintainer setup checklist.

**Important:** the translated `index.[LANGUAGE CODE].md` / `_index.[LANGUAGE CODE].md` files in `content/` are *generated* from the gettext files in `po/`. Please don't edit them by hand - your changes would be overwritten by the next sync. Translate in Weblate instead (titles, descriptions, author bios and article bodies are all available there as ordinary strings).

Tags stay in English in every article's front matter - they are shared across all languages. A tag's *display name* is translated in Weblate like any other string (it comes from `content/tags/{tagName}/_index.en.md`).

When translating in Weblate, please copy shortcodes and URLs verbatim: never translate anything inside `{{< >}}` blocks.

#### Maintainer workflow

After editing English content or merging a Weblate pull request:

```bash
python3 scripts/po_sync.py
```

then review, build and commit `po/`, `po4a/` and `content/` together. Details in [docs/weblate.md](docs/weblate.md).

#### Adding a new language

To add a new language, as described in the [blowfish documentation](https://blowfish.page/docs/configuration/#language-and-i18n):

1. Add `config/_default/languages.[LANGUAGE CODE].toml`
2. Add `config/_default/menus.[LANGUAGE CODE].toml`

Fill them to match the `en` versions of the files. Now the language should be visible in the Hugo locale picker in the top menu, and `scripts/po_sync.py` will pick it up automatically. In Weblate, use "Add new translation" in each component to start translating; only articles translated above 80% get generated.

## TODO

- [ ] Update colors to match Natalia Vish's palette
- [x] Add better tags for existing illustrations
- [x] Add `author-extra.html` partial on Author tag pages
- [ ] Implement sorting and filtering on the art page, for example using [Isotope](https://isotope.metafizzy.co/)
- [ ] Add short stories written based on the Seeds
- [ ] Add tooltips for some elements, like the theme swapper
- [x] Fix og:images and descriptions for the /art/ page and author pages
- [ ] Add some anti-AI scrapping solutions
- [ ] Add a better license filter for art