# Story Seed Library

Welcome to the repository for the [Story Seed Library](https://storyseedlibrary.org/), a copyleft library of Solarpunk art and writing!

You can contribute to it on [Codeberg](https://codeberg.org/alxd/storyseedlibrary) and [Github](https://github.com/pawelngei/storyseedlibrary) - the merged commits will be [mirrored](https://codeberg.org/Recommendations/Mirror_to_Codeberg) between the platforms!

## Theme

This page is heavily based on a modified [blowfish](https://blowfish.page/) theme by Nuno Coração. The forked repository is configured as a submodule, available on [Codeberg]() and [Github](https://github.com/pawelngei/blowfish) (mirrored).

## Contributing

Please install Hugo (`v0.145.0`) and try previewing your changes with `hugo serve -w` before you make a Pull Request!

### Adding Authors

To add a new author:

1. Create a new file in `data/authors/{authorName}.json` and configure it similarly to other authors. It will control the `author-extra.html` box rendered on content pages.
2. Add a new catalog and file in `content/authors/{authorName}/_index.md`. It will configure the "category" page for the author and what name will be displayed on their content cards.
3. Now you can add the author in specific content articles. One article can have multiple authors, like:
  ```
  authors:
    - alxd
    - {authorName}
  ```

### Adding Art / Pages

To add new art by an existing / newly created author:

1. Create a new catalog in `content/{contentType}/{authorName}{urlSlug}/`, for example `content/art/the-lemonaut-community-center`.
2. Inside, create an `index.md` file with the content of the page / description and license of the art, listing the authors.
3. Save the high quality art as `featured.jpg` (not PNG or any other file) in the same catalog. It will be automatically scaled to different resolutions by hugo, and the original will be available once the user clicks the Full Resolution button.

### Adding Tags

To add a new tag:

1. Create a new file `content/tags/{tagName}/_index.md` which will determine the name and description of the tag, as well as how it will be displayed on cards.
2. Modify the content `index.md` by adding the `{tagName}` to specific lists, like:
  ```
  tags: ["illustration", "CC BY-SA 4.0", "my new tag"]
  ```
3. All spaces in the tag name are translated to `-` by Hugo.

## TODO

- [ ] Update colors to match Natalia Vish's palette
- [ ] Add better tags for existing illustrations
- [ ] Add `author-extra.html` partial on Author tag pages
- [ ] Implement sorting and filtering on the art page, for example using [Isotope](https://isotope.metafizzy.co/)
- [ ] Add short stories written based on the Seeds
- [ ] Add tooltips for some elements, like the theme swapper
- [ ] Fix og:images and descriptions for the /art/ page and author pages
- [ ] Add some anti-AI scrapping solutions
- [ ] Add a better license filter for art