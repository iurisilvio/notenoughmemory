#!/usr/bin/env python

# Basic settings

from decouple import config

AUTHOR = u"Iuri de Silvio"
SITENAME = u"iurisilvio"
SITEURL = "https://iurisilv.io"
RELATIVE_URLS = config('RELATIVE_URLS', cast=bool, default=True)

PATH = "source"
OUTPUT_PATH = "output/"

TIMEZONE = "America/Sao_Paulo"

ARTICLE_EXCLUDES = ("pages", "drafts", "extra")

# URL settings

ARTICLE_SAVE_AS = ARTICLE_URL = "{date:%Y}/{date:%m}/{slug}.html"
ARTICLE_LANG_URL = "{lang}/" + ARTICLE_URL
ARTICLE_LANG_SAVE_AS = "{lang}/" + ARTICLE_SAVE_AS
AUTHOR_SAVE_AS = AUTHOR_URL = "author/{slug}.html"
CATEGORY_SAVE_AS = CATEGORY_URL = "category/{slug}.html"
TAG_SAVE_AS = TAG_URL = "tag/{slug}.html"


# Date format and locale

# Feed settings

FEED_DOMAIN = SITEURL

FEED_ATOM = "feed/atom.xml"
FEED_RSS = "feed/rss.xml"

CATEGORY_FEED_ATOM = "feed/category/{slug}." + FEED_ATOM
CATEGORY_FEED_RSS = "feed/category/{slug}." + FEED_RSS

TAG_FEED_ATOM = "feed/tag/{slug}." + FEED_ATOM
TAG_FEED_RSS = "feed/tag/{slug}." + FEED_RSS

# FeedBurner

# Pagination

DEFAULT_PAGINATION = 10

# Tag cloud

# Translations

DEFAULT_LANG = "en"
TRANSLATION_FEED_ATOM = "feed/translation/{lang}.atom.xml"

# Ordering content

REVERSE_ARCHIVE_ORDER = True

# Theming

# Asset management


# Theme specific

DISQUS_SITENAME = "notenoughmemory"
# GITHUB_URL = "https://github.com/iurisilvio/notenoughmemory"
GOOGLE_ANALYTICS = "UA-33399692-1"
TWITTER_USERNAME = "iurisilvio"

# Blogroll
LINKS = (
    ("ceps.io", "https://ceps.io"),
    ("postmon", "https://www.postmon.com.br"),
    ("Django contributor", "https://code.djangoproject.com/query?owner=iurisilvio&or&reporter=iurisilvio&col=id&col=summary&col=owner&col=status&col=reporter&col=type&order=priority"),
    ("bottle-sqlalchemy", "https://github.com/iurisilvio/bottle-sqlalchemy"),
  )

# Social widget
SOCIAL = (
    ("Twitter", "https://twitter.com/iurisilvio"),
    ("GitHub", "https://github.com/iurisilvio"),
    ("LinkedIn", "http://br.linkedin.com/in/iurisilvio"),
)

STATIC_PATHS = [
    "images",
    "extra/CNAME",
    "extra/google4e0a3411175d335b.html",
]
EXTRA_PATH_METADATA = {
    'extra/CNAME': {'path': 'CNAME'},
    'extra/google4e0a3411175d335b.html': {'path': 'google4e0a3411175d335b.html'},
}

PLUGIN_PATHS = ['../externals/pelican-plugins/']
PLUGINS = ['sitemap']

SITEMAP = {
    'format': 'xml',
}
