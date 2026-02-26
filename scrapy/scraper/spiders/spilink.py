import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy_playwright.page import PageMethod

class SpilinkSpider(CrawlSpider):
    name = "spilink"
    allowed_domains = ["albumoftheyear.org"]
    def start_requests(self):
        yield scrapy.Request(
            "https://www.albumoftheyear.org/",
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "span#homeNewReleases")
                ],
            }
        )

    rules = (
        Rule(LinkExtractor(restrict_css='span#homeNewReleases', allow=r'/artist/'), follow=True, process_request='use_playwright'),
        Rule(LinkExtractor(allow=r'/?type=lp'), callback='parse_artist', follow=False, process_request='use_playwright')
    )

    def use_playwright(self, request, response):
        request.meta['playwright'] = True
        return request

    def parse_artist(self, response):
        artist = response.css("h1.artistHeadline::text").get()
        releases = response.css("div.albumBlock.small")
        for release in releases:
            title = release.css(".albumTitle.normal::text").get()
            year = release.css(".type::text").get()
            year = year[0:4]
            yield {"Artist ": artist, "Title ": title, "Year ": year}

