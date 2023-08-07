import scrapy


class HardwareonlineSpider(scrapy.Spider):
    name = "hardwareonline"
    allowed_domains = ["www.hardwareonline.dk"]
    start_urls = ["https://www.hardwareonline.dk/forum_list.aspx?fid=23"]

    def parse(self, response):
        pass
