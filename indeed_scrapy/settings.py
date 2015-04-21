# -*- coding: utf-8 -*-

# Scrapy settings for indeed_scrapy project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import os
BOT_NAME = 'indeed_scrapy'

SPIDER_MODULES = ['indeed_scrapy.spiders']
NEWSPIDER_MODULE = 'indeed_scrapy.spiders'

ITEM_PIPELINES = {
    'indeed_scrapy.pipelines.CSVWithEncodingPipeline': 300,
}

LOG_LEVEL = 'INFO'

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': None,
    'indeed_scrapy.middlewares.custom_redirect.CustomRedirectMiddleware': 100,
}

API_KEY = '9e56e79f3fa14e4286cc6c7a820b6175'

# comment lines if run not in scrapinghub
# SPIDER_MIDDLEWARES = {
#     'indeed_scrapy.middlewares.deltafetch.DeltaFetch': True,
# }

# DELTAFETCH_ENABLED = True
# DELTAFETCH_DIR = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')

# uncomment if need full scraping
# FULL_SCRAPING = 1

# Number of days. (Use for receiving data from the last N days)
# DAYS = 1

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'indeed_scrapy (+http://www.yourdomain.com)'
