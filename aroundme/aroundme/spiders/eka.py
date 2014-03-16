#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from scrapy.spider import Spider  
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from aroundme.items import EkaStoreListItem
import re
import urlparse
import sys
 
class EkaSpider(Spider):
    reload(sys)
    sys.setdefaultencoding('utf-8') 
    name = "eka"  
    allowed_domains = ["eka.cn"]  
    start_urls = [  
        "http://www.eka.cn/index.php?app=shop&city=64"  
    ]
    global crawledUrls
    crawledUrls = ["http://www.eka.cn/index.php?app=shop&city=64"]

    def isStoreListPage(self, sel):
        return sel.xpath('//div[@class="store_con"]') != []
    
    def isBusinessCardPage(self, sel):
        return sel.xpath('//div[@class="business_card"]') != []
    
    def get_query_strings(self, url):
        query = urlparse.urlparse(url).query
        return dict([(k,v[0]) for k,v in urlparse.parse_qs(query).items()])
    
    def remove_spaces(self, str):
        return str.replace(' ','').replace(' ','').replace('\r', '').replace('\t', '').replace('\n', '')
    
    def parse(self, response):  
        sel = Selector(response)
        base_url = get_base_url(response)
        cities = sel.xpath('//ul/li[@class="city_li"]/a/@href').extract()  
        categories = sel.xpath('//div[@id="merchant_left01"]/div[@class="category02"]/a/@href').extract()  
        items = []
        
        if self.isStoreListPage(sel) :
            store = sel.xpath('//div[@class="store_con"]/div[@class="detail"]/div[@class="detail_con left"]')
            storeCount = len(store.xpath('div[@class="detail_title"]').extract())
            if storeCount > 0:
                for i in range(storeCount):
                    #===================================================================
                    # item['name'] = store.xpath('div[@class="detail_title"]/div[@class="left"]/a/text()').extract()[i].strip()
                    # tmpAddress = store.xpath('div[@class="detail_addr"]/text()').extract()[i].strip()
                    # item['address'] = re.sub(u'^地址：', '', tmpAddress)
                    # tmpContactPhone = store.xpath('div[@class="detail_tel"]/text()').extract()[i].strip()
                    # item['contact_phone'] = re.sub(u'^电话：', '', tmpContactPhone)
                    # item['fromUrl'] = response.url
                    # item['storeDetailUrl'] = store.xpath('div[@class="detail_title"]/div[@class="left"]/a/@href').extract()[i].strip()
                    # items.append(item)
                    #===================================================================
                    url = store.xpath('div[@class="detail_title"]/div[@class="left"]/a/@href').extract()[i].strip()
                    if 'http://' not in url:
                        url = urljoin_rfc(base_url, url)
                    if url not in crawledUrls:
                        crawledUrls.append(url)
                    items.extend([self.make_requests_from_url(url).replace(callback=self.parse)])
        elif self.isBusinessCardPage(sel):
            item = EkaStoreListItem()
            item['fromUrl'] = response.url
            qs = self.get_query_strings(response.url)
            item['externalId'] = qs['id']
            brandpos = sel.xpath('//div[@class="brand_position"]//text()')
            if len(brandpos) > 0:
                tmp = brandpos[len(brandpos) - 1].extract()
                item['name'] = tmp.replace('>', '').strip()
            lines = sel.xpath('//div[@class="business_card02_left01"]/dl/dd[@class="left"]//text()').extract()
            i=0
            while i < len(lines):
                line = lines[i].strip()
                if self.remove_spaces(line).startswith(u'主营:'):
                    i = i + 1
                    item['main_business'] = lines[i].strip()
                elif line.startswith(u'详细地址:'):
                    i = i + 1
                    item['address'] = lines[i].strip()
                elif line.startswith(u'联系电话:'):
                    i = i + 1
                    item['contact_phone'] = lines[i].strip()
                elif line.startswith(u'营业时间:'):
                    i = i + 1
                    item['opening_hours'] = lines[i].strip()
                elif line.startswith(u'消费规则:'):
                    i = i + 1
                    item['consumer_rules'] = lines[i].strip()
                elif line.startswith(u'特约合作:'):
                    i = i + 1
                    item['special_cooperation'] = lines[i].strip()
                elif line.startswith(u'加入时间:'):
                    i = i + 1
                    item['join_date'] = lines[i].strip()
                elif self.remove_spaces(line).startswith(u'人气'):
                    i = i + 1
                    item['popularity'] = lines[i].strip()
                i = i + 1
            items.append(item)
        else:
            for cityUrl in cities:
                if 'http://' not in cityUrl:
                    url = urljoin_rfc(base_url, cityUrl)
                else:
                    url = cityUrl
                if url not in crawledUrls:
                    crawledUrls.append(url)
                    items.extend([self.make_requests_from_url(url).replace(callback=self.parse)])
            for categoryUrl in categories:
                if 'http://' not in categoryUrl:
                    url = urljoin_rfc(base_url, categoryUrl)
                else:
                    url = categoryUrl
                if url not in crawledUrls:
                    crawledUrls.append(url)
                    items.extend([self.make_requests_from_url(url).replace(callback=self.parse)])

        return items
    
    