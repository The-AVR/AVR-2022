## Tooling

The generate the static site, we use the [Hugo](https://gohugo.io/)
static site generator. While not strictly needed to develop the site,
it is very nice to have installed in order to preview the site.

Make sure to install the extended version of Hugo, as we utilize some of the
asset processing functionality only in the extended version
(You may be able to install this with the `hugo-bin-extended` `npm` package.
Run it with `npx hugo` instead.)

`npm` is not required to preview the site, but it is required to build it.

Additionally we also use the [Docsy](https://docsy.dev) theme by Google for this.
This is a `git` submodule, so make sure you've initialized this repo's submodules:

```bash
git submodule update --init --recursive
```

To preview the site, `cd` into this `docs` directory and run:

```bash
hugo serve
```

This will give you a URL like this to preview the site:

```none
Environment: "development"
Serving pages from memory
Running in Fast Render Mode. For full rebuilds on change: hugo server --disableFastRender
Web Server is available at //localhost:1205/ (bind address 127.0.0.1)
Press Ctrl+C to stop
```

## Structure

Every page in this site is it's own folder. This is to allow pages to be
easily bundled with the images in the page.

The content for each page is in the file `_index.md`. While `index.md` is _also_
valid, the underscore version helps ensure that the file is at the top
of the files when sorted alphabetically.

Each page also should contain a frontmatter.

```yaml
---
title: "Page Title"
weight: 3
description: "Page description"
---
```

While the folder name for the page is the URL slug, the `title` field in the
frontmatter is how the page title actually appears. This should be wrapped
in quotes to avoid any text escaping issues. The `weight` field is used to sort the
pages. Otherwise, the pages will automatically be sorted alphabetically.
A larger weight value will make the page sort lower. Finally, the `description`
field is an optional field that will show a description of the page at the top,
of the page, and below the page URL on its parent page.

## Content

The written content is just normal Markdown. I try to keep the line lengths below
88 characters for split-screen readability.

There is some extra functionality provided by the theme, or that I like to use.

### Links

Links to external content are the same as normal Markdown.

```markdown
[10-Pack of Aluminum Standoffs (80mm)](https://www.amazon.com/uxcell-Aluminum-Standoff-Fastener-Quadcopter/dp/B01MSAHZQO/)
```

However, links to internal content should use the `relref` shortcode. This has
the added advantage of not needing to copy the full URL and automatic checks to
make sure the link is valid.

```markdown
[building your VRC drone]({{< relref "../../primary-goal/vrc-drone-assembly" >}})
```

### Keyboard Buttons

With Markdown, you can still insert arbitrary HTML. My favorite usage of this
is keyboard buttons, which is the `<kbd>` HTML tag. For example:

> Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Esc</kbd> to open Task Manager.

```html
Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Esc</kbd> to open Task Manager.
```

### Callouts

To provide callouts, you can use the `alert` shortcode like so:

```markdown
{{% alert title="Warning" color="warning" %}}
The balance connector should always be used whenever the
battery is being used with the charger.
{{% /alert %}}
```

The `title` parameter is what the callout block will be called, and the `color`
is the color of the color bar on the left side.

Here are the 4 types of callout blocks I like to use to stay consistent:

```markdown
{{% alert title="Danger" color="danger" %}}

{{% alert title="Warning" color="warning" %}}

{{% alert title="Note" color="note" %}}

{{% alert title="Tip" color="tip" %}}
```

### Images

Images are the same as normal Markdown. In our case, if you add `alt` text to an image,
it will appear as the image subtitle.

```markdown
![M4 Express being soldered](M4_soldering.jpg)
```

The `alt` text is optional, and can be omitted:

```markdown
![](pcc_combo.png)
```

### YouTube Videos

To embed a YouTube video in the page, you can use the `youtube` shortcode
with the video ID like so:

```markdown
{{< youtube 6s3Z06fJGpY >}}
```

### Cards

If you want to place something in a card, such as a link to a file, use the `card`
shortcode.

```markdown
{{< card header="**FlySky FS-i6S User Manual**" >}}
[FS-i6S-User-manual-20170706-compressed.pdf](FS-i6S-User-manual-20170706-compressed.pdf)
{{< /card >}}
```

The header can be omitted if desired.

### Banners

Similar to the `alert` shortcode, you can use the `pageinfo` shortcode to create
a banner across the page. The color options are the same as the `alert` shortcode.

```markdown
{{% pageinfo color="warning" %}}
This is placeholder content.
{{% /pageinfo %}}
```

### Other

For all other functionality, see the
[Docsy documentation](https://www.docsy.dev/docs/adding-content/shortcodes/).

## Building

To build the site, you must have `hugo` extended installed. Additionally,
you must install the required `npm` packages from this directory
(these facilitate SCSS compilation):

```bash
npm install
```

To build the website, just run:

```bash
hugo
```

This will build the site to the `public` directory. Finally, you need to run the
script `postprocess.py`.

```bash
python -m pip install -r requirements.txt
python postprocess.py
```

This script does 2 things.

1. First, this script finds all of the JS and CSS files hosted on 3rd party CDNs
   and downloads them to a local directory and rewrites the
   the HTML tag. I don't really like how the theme uses like 4 different CDNs,
   and I rather we host all of the required assets.
2. Second, this script rewrites all of the `src` attributes of the `img` tags.
   Because we use
   [Hugo Page Bundles](https://gohugo.io/content-management/page-bundles/)
   and for writer convenience, image URLS are all relative. There are some pages
   in the theme where content gets rendered in a different URL, such as the full section
   view. In these cases, the image URLS are broken. Thus, this script goes and rewrites
   all of them to be absolute URLs.
