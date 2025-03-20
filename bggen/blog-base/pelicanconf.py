#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = 'Michael Saxon'
SITENAME = 'Michael Saxon'
SITEURL = 'saxon.me/blog'

PATH = 'content'

RELATIVE_URLS = True

TIMEZONE = 'US/Pacific'
DEFAULT_DATE_FORMAT= '%B %-d, %Y'
DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/{slug}.atom.xml"
AUTHOR_FEED_ATOM = "feeds/{slug}.atom.xml"
FEED_ALL_RSS = 'feeds/all.rss.xml'
CATEGORY_FEED_RSS = 'feeds/{slug}.rss.xml'
AUTHOR_FEED_RSS = 'feeds/{slug}.rss.xml'

DEFAULT_PAGINATION = 10

# Add the plugin path
PLUGIN_PATHS = ['plugins']
PLUGINS = ["pelican_katex", "footnote_popups", "infobox", "shorten_filter"]

SLUGIFY_SOURCE = 'basename'

ARTICLE_URL = '{date:%Y}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{slug}/index.html'

PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# Add to your existing config
STATIC_PATHS = ['images', 'js', 'css', 'fonts']  # Add any other static paths you need

# Add these settings
USE_FOLDER_AS_CATEGORY = False
DISPLAY_PAGES_ON_MENU = False
PAGE_PATHS = ['pages']  # Look for pages in content/pages/
ARTICLE_PATHS = ['']    # Look for articles in content root

# Optional: Exclude pages directory from articles search
ARTICLE_EXCLUDES = ['pages']

PUBLICATIONS_SRC = 'content/pubs.bib'