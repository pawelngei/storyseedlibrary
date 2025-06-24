# Story Seed Library

Welcome to the repository for the [Story Seed Library](https://storyseedlibrary.org/), a copyleft library of Solarpunk art and writing!

You can contribute to it on [Codeberg](https://codeberg.org/alxd/storyseedlibrary) and [Github](https://github.com/pawelngei/storyseedlibrary) - the merged commits will be [mirrored](https://codeberg.org/Recommendations/Mirror_to_Codeberg) between the platforms!

## Theme

This page is heavily based on a modified [blowfish](https://blowfish.page/) theme by Nuno Coração. The forked repository is configured as a submodule, available on [Codeberg]() and [Github](https://github.com/pawelngei/blowfish) (mirrored).

## Contributing

Please install Hugo (specifically version [`0.145.0`](https://github.com/gohugoio/hugo/releases/tag/v0.145.0)) and try previewing your changes with `hugo serve -w` before you make a Pull Request!

### Adding Authors

To add a new author:

1. Create a new file in `data/authors/{authorName}.json` and configure it similarly to other authors. It will control the `author-extra.html` box rendered on content pages.
2. Add a new catalog and file in `content/authors/{authorName}/_index.en.md`. It will configure the "category" page for the author and what name will be displayed on their content cards.
3. Now you can add the author in specific content articles. One article can have multiple authors, like:
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

#### Adding a new language

To add a new language, as described in the [blowfish documentation](https://blowfish.page/docs/configuration/#language-and-i18n):

1. Add `config/_default/languages.[LANGUAGE CODE].toml`
2. Add `config/_default/manus.[LANGUAGE CODE].toml`

Fill them to match the `en` versions of the files.

Now the language should be visible in the Hugo locale picker in the top menu. By default, only the translated articles will be visible.

Each translated article URL will be prepended by your language code, like `/art` becoming `/pl/art`. Please remember that as you're using Markdown links - they cannot be 1:1 of their English versions.

#### Translating articles

In each article page, next to `index.md` or `index.en.md`, create a matching `index.[LANGUAGE CODE].md` in your language and translate it. List pages like `/art` or `/seeds` might require `_index.[LANGUAGE CODE].md` in their main catalog.

#### Translating URLs

To translate a URL of a given article, you need to give all of its language versions a [translationKey](https://gohugo.io/methods/page/translationkey/) and the translated ones a `url`, like this:

`en`
```yaml
translationKey: 'What is Solarpunk?'
```

`pl`
```yaml
translationKey: 'What is Solarpunk?'
url: 'czym-jest-solarpunk'
```

#### Translating Tags

Please don't modify the English tags associated with each article, like:

```yaml
tags: ["illustration", "CC BY-NC-SA 4.0", "horizontal", "farming", "waste"]
```

If you do, they will lose synchronization with their counterparts in other languages.

To translate a Tag correctly, just create a catalog with a tag name in `content/tags/`, like `city` - and inside place an `_index.[LANGUAGE_CODE].md` containing just:

```yaml
---
title: "Miasto"
---
```

This will translate the default `city` to `Miasto` on the Tag page and every art page.

## TODO

- [ ] Update colors to match Natalia Vish's palette
- [x] Add better tags for existing illustrations
- [ ] Add `author-extra.html` partial on Author tag pages
- [ ] Implement sorting and filtering on the art page, for example using [Isotope](https://isotope.metafizzy.co/)
- [ ] Add short stories written based on the Seeds
- [ ] Add tooltips for some elements, like the theme swapper
- [x] Fix og:images and descriptions for the /art/ page and author pages
- [ ] Add some anti-AI scrapping solutions
- [ ] Add a better license filter for art