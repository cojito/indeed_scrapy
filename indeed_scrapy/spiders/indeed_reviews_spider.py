# -*- coding: utf-8 -*-
from csv import QUOTE_NONNUMERIC
from csv import DictReader
import json
import os
import urllib2
import scrapy
from scrapy import log
from scrapy.selector import Selector
from indeed_scrapy.items import IndeedReviewItem


def get_review_urls_from_file():
    fname = 'indeed_jobs.csv'
    fpath = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')
    with open('%s/../../%s' % (fpath, fname)) as f:
        reader = DictReader(f, quoting=QUOTE_NONNUMERIC)
        for row in reader:
            if row['company_review_url']:
                yield row['company_review_url']


def get_url(api_key, project_id, spider_id, run, count, offset):
    return "http://storage.scrapinghub.com/items/%s/%s/%s/?apikey=%s&count=%s&start=%s/%s/%s/%s&format=json" % \
           (project_id, spider_id, run, api_key, count, project_id, spider_id, run, offset)


def get_data(url):
    try:
        f = urllib2.urlopen(url)
        response = json.loads(f.read())
    except urllib2.HTTPError:
        response = []
    return response


def extract_review_urls(data):
    urls = [i.get('company_review_url', '') for i in data]
    urls = set(urls)
    urls = filter(lambda x: x != '', urls)
    return urls


def get_review_urls_by_api(api_key, project_id, spider_id, run_id, count, offset):
    urls_count = 0
    url = get_url(api_key, project_id, spider_id, run_id, count, offset)
    data = get_data(url)
    urls = extract_review_urls(data)
    urls_count += len(urls)
    log.msg("all urls count: %s" % urls_count, level=log.WARNING)
    for review_url in urls:
        yield review_url


def convert_rating(rating):
    try:
        return 5.0*float(rating)/86.0
    except:
        return 0.0


def check_and_convert_ratings(ratings):
    if len(ratings) < 5:
        return [0.0, 0.0, 0.0, 0.0, 0.0]
    else:
        rates = map(lambda x: x.replace('width:', ''), ratings)
        rates = map(lambda x: x.replace('px', ''), rates)
        return map(convert_rating, rates)


class IndeedReviewsSpider(scrapy.Spider):
    name = "indeed_reviews"
    base_domain = "http://www.indeed.nl"
    allowed_domains = ["www.indeed.nl", "storage.scrapinghub.com"]
    start_urls = [base_domain]
    urls_count = 0

    def parse(self, response):
        settings = self.settings
        api_key = settings.get('API_KEY')
        project_id = settings.get('PROJECT_ID')
        spider_id = settings.get('SPIDER_ID')
        run_id = settings.get('RUN_ID')
        count = 1000
        offset = 0

        stat_url = "http://storage.scrapinghub.com/items/%s/%s/%s/stats?apikey=%s&format=json" % \
                   (project_id, spider_id, run_id, api_key)
        data = get_data(stat_url)
        counts = data['counts']['company_review_url']
        log.msg("counts: %s" % counts, level=log.WARNING)
        log.msg("counts type: %s" % type(counts), level=log.WARNING)

        while offset < counts:
            url = get_url(api_key, project_id, spider_id, run_id, count, offset)
            log.msg('url: %s' % url, level=log.WARNING)
            offset += count
            yield scrapy.Request(url, callback=self.parse_json_f)

    def parse_json_f(self, response):
        resp = json.loads(response.body_as_unicode())
        urls = extract_review_urls(resp)
        self.urls_count += len(urls)
        log.msg("all urls count: %s" % self.urls_count, level=log.WARNING)
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_review)

    def parse_review(self, response):
        # select block where
        selector = Selector(response)
        next_page = selector.css('.pagination').xpath('.//a[contains(., "Volgende")]//@href').extract()
        if next_page:
            next_page_url = self.base_domain + next_page[0]
            yield scrapy.Request(next_page_url, callback=self.parse_review)

        reviews = selector.css('.company_review_container').extract()
        company = ' '.join(selector.css('#company_name span').xpath('text()').extract()).strip().encode('utf-8')

        for review in reviews:
            review_selector = Selector(text=review)
            item = dict()

            item['company'] = company
            item['title'] = ' '.join(review_selector.css('.review_title').xpath('text()').extract()).strip().encode('utf-8')
            item['pros'] = ' '.join(review_selector.css('.review_pros').xpath('text()').extract()).strip().encode('utf-8')
            item['cons'] = ' '.join(review_selector.css('.review_cons').xpath('text()').extract()).strip().encode('utf-8')
            item['text'] = ' '.join(review_selector.css('.description').xpath('text()').extract()).strip().encode('utf-8')

            ratings = [0.0, 0.0, 0.0, 0.0, 0.0]
            ratings_popup = review_selector.css('.ratings_popup').extract()
            if ratings_popup:
                ratings_popup_selector = Selector(text=ratings_popup[0])
                ratings = ratings_popup_selector.css('span.rtg_i.rating').xpath('@style').extract()
                ratings = check_and_convert_ratings(ratings)

            item['work_life_balance'] = ratings[0]      # Work/Life Balance (Privé-Werk Balans)
            item['comp_benefits'] = ratings[1]          # Comp & Benefits (Vergoeding/Arbeidsvoorwaarden)
            item['security'] = ratings[2]               # Job Security/Advancement (Ontwikkelingsmogelijkheden)
            item['management'] = ratings[3]             # Management (Leiderschap)
            item['culture_values'] = ratings[4]         # Culture & Values (Werksfeer)

            yield IndeedReviewItem(**item)
