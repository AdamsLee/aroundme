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
    global cityDict
    cityDict = {}
    
    def getCityDict(self, sel, base_url):
        cityLinks = sel.xpath('//ul/li[@class="city_li"]/a/@href').extract()
        cityNames = sel.xpath('//ul/li[@class="city_li"]/a//text()').extract()
        if len(cityLinks) == len(cityNames):
            i=0
            while i < len(cityLinks):
                url = urljoin_rfc(base_url, cityLinks[i])
                qs = self.get_query_strings(url)
                cityId = qs['city']
                if cityId != '':
                    cityDict[cityId] = cityNames[i]
                i = i + 1
    
    def isStoreListPage(self, sel):
        return sel.xpath('//div[@class="store_con"]') != []
    
    def isBusinessCardPage(self, sel):
        return sel.xpath('//div[@class="business_card"]') != []
    
    def get_query_strings(self, url):
        query = urlparse.urlparse(url).query
        return dict([(k,v[0]) for k,v in urlparse.parse_qs(query).items()])
    
    def remove_spaces(self, str):
        return str.replace(' ','').replace(' ','').replace('\r', '').replace('\t', '').replace('\n', '')
    
    def crawl_url(self, base_url, url, items):
        if 'http://' not in url:
            url = urljoin_rfc(base_url, url)
        if url not in crawledUrls:
            crawledUrls.append(url)
            items.extend([self.make_requests_from_url(url).replace(callback=self.parse)])
    
    def crawl_store_info_from_biz_card_page(self, respUrl, sel):
        item = EkaStoreListItem()
        item['fromUrl'] = respUrl
        qs = self.get_query_strings(respUrl)
        item['externalId'] = qs['id']
        item['city_name'] = cityDict[qs['city']]
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
        return item
    
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
                    url = store.xpath('div[@class="detail_title"]/div[@class="left"]/a/@href').extract()[i].strip()
                    self.crawl_url(base_url, url, items)
            
            storePageLinks = sel.xpath('//div[@class="store_page"]/div/div/a')
            storePageLinkCount = len(storePageLinks)
            if storePageLinkCount > 3:
                url = storePageLinks[storePageLinkCount - 1].xpath('@href').extract()[0]
                self.crawl_url(base_url, url, items)
            
        elif self.isBusinessCardPage(sel):
            item = self.crawl_store_info_from_biz_card_page(response.url, sel)
            items.append(item)
        else:
            if cityDict == {}:
                self.getCityDict(sel, base_url)
                
            for cityUrl in cities:
                self.crawl_url(base_url, cityUrl, items)
                
            for categoryUrl in categories:
                self.crawl_url(base_url, categoryUrl, items)
                
        return items
    
    