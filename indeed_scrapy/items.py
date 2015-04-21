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
    outer_link_url = scrapy.Field()
    company_review_url = scrapy.Field()


class IndeedReviewItem(scrapy.Item):
    url = scrapy.Field()
    company = scrapy.Field()
    title = scrapy.Field()
    pros = scrapy.Field()
    cons = scrapy.Field()
    text = scrapy.Field()
    comp_benefits = scrapy.Field()          # Comp & Benefits (Vergoeding/Arbeidsvoorwaarden)
    work_life_balance = scrapy.Field()      # Work/Life Balance (Privé-Werk Balans)
    management = scrapy.Field()             # Management (Leiderschap)
    culture_values = scrapy.Field()         # Culture & Values (Werksfeer)
    security = scrapy.Field()               # Job Security/Advancement (Ontwikkelingsmogelijkheden)
