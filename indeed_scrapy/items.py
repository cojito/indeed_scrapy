# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IndeedJobItem(scrapy.Item):
    url = scrapy.Field()
    company = scrapy.Field()
    job_text = scrapy.Field()
    link_url = scrapy.Field()
    company_review_url = scrapy.Field()
