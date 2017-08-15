# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import time
import redis
from cnki.settings import REDIS
import json

re = redis.Redis(host=REDIS.get('host'), port=REDIS.get('port'), db=REDIS.get('db'))


class KbsSpider(scrapy.Spider):
    name = 'kbs'
    allowed_domains = ['cnki.net']
    start_urls = ['http://kbs.cnki.net/']


    def parse(self, response):
        for href in response.css('.more'):
            url = href.xpath('@href').extract()[0].split('?')[1]
            full_url = 'http://kbs.cnki.net/DataCenter/CommonHandler.ashx?_=' + \
                       str(int(time.time() * 1000)) + '&action=more&' + url
            yield scrapy.Request(full_url, callback=self.parse_news)

    def parse_news(self, response):
        key = str(response.body, 'utf8').split('<ul><li>')[0].split(';')[-1].strip('♂')
        print(str(key))  # 标签
        soup = BeautifulSoup(response.body, 'html.parser')
        for i in soup.ul:
            domain = i.a.attrs.get('href')
            val = i.a.attrs.get('val')

            re.hset(str(key), str(domain), json.dumps({'value': val}))
            print(i.a.attrs.get('href'))
            print(i.a.attrs.get('val'))
