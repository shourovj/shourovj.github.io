# About

Source for [saxon.me](https://saxon.me)

The site uses a heavily custom, framework-free theme for Pelican + an assortment of custom Pelican plugins to generate all main pages. This was built was an incremental migration from a 100% static HTML site.

## Blog generator setup

The generator is in the `bggen/` folder. `bggen/blog-base` holds all content, configs, etc for the site itself.
`bggen/saxon-theme` is my theme.

### Home page

Because I want the main `index.html` to be a static home page rather than a blog index page, I had to do a few tweaks.
The top-level index.html is generated from the static template `saxon-theme/templates/about.html`.

Due to the complexity of the template, we need to populate it using three different special markdown page files, `about.md`, `about_header.md`, and `news.md`, and a static html-implemented "experience section" (`saxon-theme/templates/static/experience.html`). The template fills them in as (simplified sketch):

```html
{% extends "base.html %}

<header>
{{ about.md: JOB_TITLE }} {{ about.md: AFFILIATION }}
{{ about_header.md: CONTENT }}
</header>

<article>
<h3>About</h3>

{{ about.md: CONTENT }}

<h3>Experience</h3>

{% include static/experience.html %}

<h3>News</h3>
<div newsbox>
{{ news.md: CONTENT }}
</div>
</article>

<footer>
```

The way Pelican knows which mds to read for this purpose is from their title. For example, Here's the start of `blog-base/content/pages/news.md`:

```markdown
Title: news
save_as:

12/13/2024 Presented our work on meta-evaluation of text-to-image metrics at NeurIPS! [paper]

11/13/2024 Presented our work on long-context capabilities in VLMs at EMNLP! [paper]

...
```

The `Title` metadata tag is how `about.html` finds the contents to populate `news`. `save_as: [blank]` is how Pelican knows to not generate a full page from this content. To make it all work, the top level `content/pages/about.md` is:

```markdown
Title: About
save_as: index.html
Template: about
remove_footnote_section: true
my_title: Ph.D. Candidate
my_affiliation: University of California, Santa Barbara

...
```

`save_as: index.html` is what tells Pelican to save it as index.html on the top level of the site (it's annoying we have to do it this way but important, as we'll discuss later).

`Template: about` is how Pelican knows to use our `about.html` rather than `page.html`. `my_title` and `my_affiliation` populate the top of the page.

### Publications page

I heavily forked Vlad Niculae's `pelican_bibtex.py` plugin. I pretty much completely rewrote the logic for generating entries because I don't actually need a fully-styled citation, I just need to pull out the venue name, date, title, authors, etc. It generates the publications page from standard BibTex with support for several special bibkeys I use to add extra content:

- `url_official`, `url_pdf`, `url_arxiv`: links to abstracts and pdfs which get filled in by a preference order
- `venue_abbrev`: the short-form name for the venue (eg,. COLM 2024) for simple readable listing of venues (rather than "Proc. of the 11th conference on xyz"
- `demo`, `video_link`, `github`, `huggingface`: self-explanatory, way to add link badges to related content
- `yindex`: hack to force ordering of the entries within a year (rather than alphabetization), since not all entries contain month/day info
- `routing`: if I add `workshop` it puts the paper in a non-archival section rather than the top
- `additional_info`: text to populate badges for stuff like spotlight, best paper, or conference orals

### Other plugins

#### Infobox

`plugins/infobox/`: my custom implementation of github-flavored infoboxes like:

> [!note]
> 
> lmao

Uses beautifulsoup to postprocess the HTML into custom infobox classes in `style.css`

#### Image processing

`plugins/image_processor.py`: grabs web url images in the `Image: ` key of a post and applies a dithering recolor using opencv to map the image into my site colorscheme, then saves this image and replaces the Image: key with this edited one.

#### Popup footnotes

`plugins/footnote_popups/`: copies and inserts the content of each footnote inline in the document inside a mouseover popup. Fancy logic in `saxon-theme/static/js/popups.js` handles centering to make sure all popups are inside the page, but as near to being centered over the mouseover zone as possible.

Also supports hiding the end-of-document footnotes and backlinks to use the popups alone with the `remove_footnote_section: true` tag at the beginning of the page's markdown

#### Reading time

`plugins/ert.py` taken as is from [nogaems](https://github.com/nogaems/pelican-ert/blob/master/ert.py)

### Other theme details

- Dark/light mode using CSS variables for the Kanagawa nvim scheme; `saxon-theme/static/js/theme.js` handles switching the color and maintaining it across instances.
- Copyable code blocks: `saxon-theme/static/js/copy-code.js` provides a click-to-copy button in each code block.
- Table of contents: `saxon-theme/static/js/toc.js` provides collapsibility to the optional table of contents (inserted into a post using `[TOC]`
