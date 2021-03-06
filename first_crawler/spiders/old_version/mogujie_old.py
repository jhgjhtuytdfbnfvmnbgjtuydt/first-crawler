import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from first_crawler.items import FashionItem
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
import pymongo
from pymongo import MongoClient
import time


class MogujieSpider (CrawlSpider):
    name = 'mogujie_old'
    allowed_domains = ['mogujie.com']
    start_urls = ["http://www.mogujie.com/"]

    # Test Links
    #start_urls = ["http://shop.mogujie.com/1qfnyw/list/index?categoryId=20005650&order=sale&shopwebtag=1&mt=10.6464.r78321&ptp=1.BtWxRgdy._mt-6464-r78321.1.FvR1m"]
    #start_urls = ["http://www.mogujie.com/book/clothing/50003?from=hpc_2"]

    rules = (
        Rule(LinkExtractor( allow = ("http://www.mogujie.com/book/", "http://shop.mogujie.com/", "http://act.mogujie.com/", "http://list.mogujie.com/"), deny = ("http://shop.mogujie.com/detail/",)), follow = True), # follow = True !!
        Rule(LinkExtractor( allow = ("http://shop.mogujie.com/detail/",)), callback = 'parse_item', follow = True),
    )

    client = MongoClient()
    db = client.fashion


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse, meta={
                'splash': {
                    'endpoint': 'render.html'
                }
            })

    def parse_item(self, response):
        # Check the duplicate
        mongo = self.db.url
        url_trim = response.url.split('?')[0]
        if mongo.find_one({"url": url_trim}):
    	    print "&&&&&&&&&&&&&&&&&&&&&&&&& This URL has been crawled &&&&&&&&&&&&&&&&&&&&&&&&&"
    	    return

        # Insert the new link into MongoDB
        newone = {
            "url": url_trim,
            "time": time.time(),
        }
        mongo.insert_one(newone)

        page = Selector(response)
        title = page.xpath('//span[@itemprop="name"]/text()').extract_first()
        images = page.xpath('//img[@id="J_BigImg"]/@src').extract_first()
        availability = page.xpath('//dd[@class="num clearfix"]/div[@class="J_GoodsStock goods-stock fl"]/text()').extract_first()
        status = response.status

        item = FashionItem()
        item['url'] = url_trim
        item['title'] = title.encode('utf-8')
        item['images'] = images
        item['availability'] = availability.encode('utf-8')
        item['status'] = status
        return item
