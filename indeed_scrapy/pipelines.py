# -*- coding: utf-8 -*-
import os
import csv
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class CSVWithEncodingPipeline(object):
    def __init__(self):
        self.file = None
        self.writer = None

    def process_item(self, item, spider):
        if self.file is None:
            fname = '%s.csv' % spider.name
            mode = 'w'
            if os.path.exists(fname):
                mode = 'a'
            self.file = open(fname, mode)
            self.writer = csv.DictWriter(self.file, fieldnames=item.keys(), quoting=csv.QUOTE_NONNUMERIC)
            if mode == 'w':
                self.writer.writeheader()

        self.writer.writerow(item)
        return item

    def spider_closed(self, spider):
        self.file.close()
