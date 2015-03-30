# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from readability.readability import Document
from indeed_scrapy.items import IndeedJobItem


class IndeedJobsSpiderSpider(scrapy.Spider):
    name = "indeed_jobs"
    base_domain = "http://www.indeed.nl"
    allowed_domains = ["www.indeed.nl"]
    start_urls = ['http://www.indeed.nl/vacatures-in-Netherlands']

    def parse(self, response):
        # select block where
        selector = Selector(response)
        search_results = selector.css('.row.result').extract()

        next_page = selector.css('.pagination').xpath('.//a[contains(., "Volgende")]//@href').extract()
        if next_page:
            next_page_url = self.base_domain + next_page[0]
            yield scrapy.Request(next_page_url, callback=self.parse)

        for result in search_results:
            res_selector = Selector(text=result)
            company = ' '.join(res_selector.css('.company span').xpath('text()').extract()).strip().encode('utf-8')
            link_url = ' '.join(res_selector.css('.jobtitle a').xpath('@href').extract()).strip().encode('utf-8')
            link_url = self.base_domain + link_url
            company_review_url = ' '.join(res_selector.xpath('//a[contains(@href,"/reviews") and (contains(text(),"reviews") or contains(text(),"review"))]//@href').extract()).strip().encode('utf-8')
            if company_review_url:
                company_review_url = self.base_domain + company_review_url

            # Parse job text by link_url
            # request = scrapy.Request(link_url, callback=self.parse_job_text_1)

            # Parse job text by job key from link_url.
            jk = link_url.split('?')
            jk = jk[1]
            viewjob_url = self.base_domain + '/viewjob?' + jk
            request = scrapy.Request(viewjob_url, callback=self.parse_job_text_2)

            request.meta['item'] = {
                'url': '',
                'company': company,
                'job_text': '',
                'link_url': link_url,
                'company_review_url': company_review_url if company_review_url else ''
            }

            yield request

    def parse_job_text_1(self, response):
        """
            Parse job text by link_url.
            :param response:
            :return:
        """
        item = response.meta['item']

        item['url'] = response.url

        html = response.body
        item['job_text'] = Document(html).summary()
        yield IndeedJobItem(**item)

    def parse_job_text_2(self, response):
        """
            Parse job text by job key from link_url.
            :param response:
            :return:
        """
        item = response.meta['item']

        item['url'] = response.url

        selector = Selector(response)
        item['job_text'] = ' '.join(selector.css('.summary').xpath('text()').extract()).strip().encode('utf-8')
        yield IndeedJobItem(**item)