# -*- coding: utf-8 -*-
import urlparse
import scrapy
from scrapy.selector import Selector
from indeed_scrapy.items import IndeedJobItem
from scrapy import log

ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

PROVINCES = ['Gelderland', 'Groningen',
             'Drenthe', 'Zeeland',
             'Limburg', 'Overijssel',
             'Noord-Brabant', 'Noord-Holland',
             'Utrecht', 'Flevoland',
             'Friesland', 'Zuid-Holland']


def get_url(letter):
    return "http://www.indeed.nl/browsejobs/Companies/%s" % letter.upper()


def get_company_urls():
    for i in ALPHABET[:]:
        yield get_url('%s' % i)


def get_urls_with_province(url):
    for province in PROVINCES:
        yield url.replace('vacatures', 'vacatures-in-Nederland-%s' % province)


def convert_count(search_count):
    try:
        search_count = search_count.split('van')
        search_count = search_count[1].strip()
        search_count = search_count.replace('.', '')
        search_count = int(search_count)
    except:
        search_count = None

    return search_count



class IndeedJobsSpider(scrapy.Spider):
    name = "indeed_jobs"
    base_domain = "http://www.indeed.nl"
    allowed_domains = ["www.indeed.nl"]
    start_urls = ["http://www.indeed.nl"]

    def parse(self, response):
        settings = self.settings
        self.full_scraping = settings.getbool('FULL_SCRAPING')

        self.days = settings.getint('DAYS', 1)
        if self.full_scraping:
            log.msg("MODE: FULL_SCRAPING", level=log.INFO)
        else:
            log.msg("MODE: ONLY NEW ITEMS SCRAPING", level=log.INFO)

        if self.full_scraping:
            for url in get_company_urls():
                yield scrapy.Request(url, callback=self.parse_by_company_name)
        else:
            query = '?q='
            query += '&l=Netherlands'
            query += '&fromage=%s' % self.days
            query += '&sort=date'
            url = self.base_domain + '/vacatures'
            url = url + query
            print url
            yield scrapy.Request(url, callback=self.check_search_count)

    def parse_by_company_name(self, response):
        # select block where
        selector = Selector(response)
        company_urls = selector.css('#companies').xpath('//p[@class="company"]//a[@class="companyTitle"]//@href').extract()

        for company_url in company_urls:
            url = self.base_domain + company_url
            yield scrapy.Request(url, callback=self.check_search_count)

    def check_search_count(self, response):
        # select block where
        selector = Selector(response)

        parse_company = True

        if self.full_scraping:
            search_count = ' '.join(selector.css('#searchCount').xpath("text()").extract()).strip().encode('utf-8')
            search_count = convert_count(search_count)

            if not search_count:
                return

            if search_count > 1000:
                if 'vacatures-in' not in response.url:
                    parse_company = False
                    log.msg("Search result > 1000. Add province to search. COUNT: %s. URL: %s" % (search_count, response.url), level=log.WARNING)
                    for url in get_urls_with_province(response.url):
                        yield scrapy.Request(url, callback=self.check_search_count)
                else:
                    log.msg("Search result with province > 1000. COUNT: %s. URL: %s" % (search_count, response.url), level=log.CRITICAL)

        if parse_company:
            next_page = selector.css('.pagination').xpath('.//a[contains(., "Volgende")]//@href').extract()

            if next_page:
                next_page_url = self.base_domain + next_page[0]
                yield scrapy.Request(next_page_url, callback=self.check_search_count)

            search_results = selector.css('.row.result').extract()
            for result in search_results:
                res_selector = Selector(text=result)
                link_url = ' '.join(res_selector.css('.jobtitle a').xpath('@href').extract()).strip().encode('utf-8')
                link_url = self.base_domain + link_url
                company_review_url = ' '.join(res_selector.xpath('//a[contains(@href,"/reviews") and (contains(text(),"reviews") or contains(text(),"review"))]//@href').extract()).strip().encode('utf-8')
                if company_review_url:
                    company_review_url = self.base_domain + company_review_url

                # Parse job text by link_url
                # request = scrapy.Request(link_url, callback=self.parse_job_text_1)

                # Parse job text by job key from link_url.
                url_params = urlparse.parse_qs(urlparse.urlparse(link_url).query)
                if 'jk' in url_params:
                    viewjob_url = self.base_domain + '/viewjob?jk=' + url_params['jk'][0]
                else:
                    viewjob_url = self.base_domain + link_url
                request = scrapy.Request(viewjob_url, callback=self.parse_job_text)

                request.meta['item'] = {
                    'url': '',
                    'company': '',
                    'job_text': '',
                    'link_url': link_url,
                    'outer_link_url': '',
                    'company_review_url': company_review_url if company_review_url else ''
                }

                yield request

    def parse_job_text(self, response):
        """
            Parse job text by job key from link_url.
            :param response:
            :return:
        """
        item = response.meta['item']

        item['url'] = response.url
        selector = Selector(response)

        if not item['company']:
            item['company'] = ' '.join(selector.css('#job_header').xpath('//span[@class="company"]//text()').extract()).strip().encode('utf-8')
        item['job_text'] = ' '.join(selector.css('.summary').xpath('text()').extract()).strip().encode('utf-8')

        request = scrapy.Request(item['link_url'], callback=self.parse_outer_link_url)
        request.meta['item'] = item
        request.meta['dont_redirect'] = True
        request.meta["handle_httpstatus_list"] = [302]
        yield request

    def parse_outer_link_url(self, response):
        item = response.meta['item']
        item['outer_link_url'] = response.headers['Location']
        yield IndeedJobItem(**item)