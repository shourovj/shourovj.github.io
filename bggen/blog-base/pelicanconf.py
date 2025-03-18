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



# Blogroll
LINKS = (('Pelican', 'https://getpelican.com/'),
         ('Python.org', 'https://www.python.org/'),
         ('Jinja2', 'https://palletsprojects.com/p/jinja/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

# Add the plugin path
PLUGIN_PATHS = ['plugins']
PLUGINS = ["pelican_katex", "footnote_popups", "infobox"]

SLUGIFY_SOURCE = 'basename'

ARTICLE_URL = '{date:%Y}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{slug}/index.html'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# Add to your existing config
STATIC_PATHS = ['images', 'js', 'css', 'fonts']  # Add any other static paths you need