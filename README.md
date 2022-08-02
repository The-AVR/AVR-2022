# Documentation

First off, I recommend cloning this `docs` branch into a seperate checkout entirely:

```bash
git clone --branch docs --recurse-submodules https://github.com/bellflight/AVR-2022 AVR-2022-Docs
```

## Tooling

The generate the static site, we use the [Hugo](https://gohugo.io/)
static site generator. While not strictly needed to write content for the site,
it is very nice to have installed in order to preview the site.

The site based on the [Docsy](https://docsy.dev) theme by Google.
To build or preview the site, make sure you have `npm` and `node` version 16+ installed.
To install all the dependencies (including the Docsy theme), simply run:

```bash
npm install
```

To preview the site, run:

```bash
npm run server
```

This will automatically open your default web browser to a live-reloading
version of the site running on your machine.

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
[building your AVR drone]({{< relref "../../primary-goal/avr-drone-assembly" >}})
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
FS-i6S-User-manual-20170706-compressed.pdf
{{< /card >}}
```

The header can be omitted if desired.

### Static Files

Please put static files like PDF manuals in the `static/files` folder and be sure
to link to it with the `static` shortcode:

```markdown
{{< static "digital version here." "456_RDX-1_Pro_Manual_V14.pdf" >}}
```

The first parameter is the text of the link,
and the second parameter is the actual filename.

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

To build the website, just run:

```bash
npm run build
```
