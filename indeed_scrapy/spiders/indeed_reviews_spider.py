# -*- coding: utf-8 -*-
from csv import QUOTE_NONNUMERIC
from csv import DictReader
import os
import scrapy
from scrapy.selector import Selector
from indeed_scrapy.items import IndeedJobItem, IndeedReviewItem


def get_review_urls():
    fname = 'indeed_jobs.csv'
    fpath = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')
    with open('%s/../../%s' % (fpath, fname)) as f:
        reader = DictReader(f, quoting=QUOTE_NONNUMERIC)
        for row in reader:
            if row['company_review_url']:
                yield row['company_review_url']


class IndeedReviewsSpider(scrapy.Spider):
    name = "indeed_reviews"
    base_domain = "http://www.indeed.nl"
    allowed_domains = ["www.indeed.nl"]
    start_urls = [base_domain]

    def parse(self, response):
        for url in get_review_urls():
            yield scrapy.Request(url, callback=self.p)

    def parse_review(self, response):


        # # select block where
        # selector = Selector(response)
        # search_results = selector.css('.row.result').extract()
        #
        # next_page = selector.css('.pagination').xpath('.//a[contains(., "Volgende")]//@href').extract()
        # if next_page:
        #     next_page_url = self.base_domain + next_page[0]
        #     yield scrapy.Request(next_page_url, callback=self.parse)
        #
        # for result in search_results:
        #     res_selector = Selector(text=result)
        #     company = ' '.join(res_selector.css('.company span').xpath('text()').extract()).strip().encode('utf-8')
        #     link_url = ' '.join(res_selector.css('.jobtitle a').xpath('@href').extract()).strip().encode('utf-8')
        #     link_url = self.base_domain + link_url
        #     company_review_url = ' '.join(res_selector.xpath('//a[contains(@href,"/reviews") and (contains(text(),"reviews") or contains(text(),"review"))]//@href').extract()).strip().encode('utf-8')
        #     if company_review_url:
        #         company_review_url = self.base_domain + company_review_url

        return IndeedReviewItem(url=response.url)
