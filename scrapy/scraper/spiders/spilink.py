import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
from scrapy_playwright.page import PageMethod

class SpilinkSpider(CrawlSpider):
    name = "spilink"
    allowed_domains = ["albumoftheyear.org"]
    def start_requests(self):
        yield scrapy.Request(
            "https://www.albumoftheyear.org/decade/2020s/releases/",
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "div#facetContent.facetContent")
                ],
            }
        )

    rules = (
        Rule(LinkExtractor(allow=r'/album/'), callback='parse_album', follow=False, process_request='use_playwright'),
    )

    def use_playwright(self, request, response):
        request.meta['playwright'] = True
        return request

    def parse_album(self, response):
        headline = response.css("div.albumHeadline")
        artists = headline.css("div.artist *::text").getall()
        artist = "".join(artists)
        album = headline.css("h1.albumTitle span::text").get()
        must_hear = headline.css("div[class^='mustHearButton']::attr(title)").get()

        critic = response.css("div.albumCriticScoreBox")
        critic_score = critic.css("div.albumCriticScore a::attr(title)").get()
        critic_score_rounded = critic.css("div.albumCriticScore a::text").get()
        critic_review_count = critic.css("div.text.numReviews span::text").get()
        critic_rating_info = critic.css("div.text.gray *::text").getall()
        critic_year_placement = None
        critic_year_end_rank = None
        if len(critic_rating_info) > 0:
            critic_year_placement = critic_rating_info[1][1:]
        if len(critic_rating_info) > 3:
            critic_year_end_rank = critic_rating_info[4][1:]

        user = response.css("div.albumUserScoreBox")
        user_score = user.css("div.albumUserScore a::attr(title)").get()
        user_score_rounded = user.css("div.albumUserScore a::text").get()
        user_rating_count = user.css("div.text.numReviews a::text").get()
        user_rating_info = user.css("div.text.gray *::text").getall()
        user_year_placement = None
        user_all_time_placement = None
        user_year_end_rank = None
        if len(user_rating_info) > 0:
            user_year_placement = user_rating_info[1][1:]
        if len(user_rating_info) > 2:
            if "Year-End" in user_rating_info[2]:
                user_year_end_rank = user_rating_info[3][1:]
            else:
                user_all_time_placement = user_rating_info[3][1:]
        if len(user_rating_info) > 4:
            user_year_end_rank = user_rating_info[5][1:]

        yield {
            "Artist ": artist, 
            "Album ": album, 
            "Must Hear Status ": must_hear if must_hear else None,
            "Critic Score" : critic_score,
            "Critic Score (Rounded) ": critic_score_rounded,
            "Critic Review Count ": critic_review_count,
            "Yearly Chart Position (Critic) ": critic_year_placement,
            "Year-End Rank (Critic)": critic_year_end_rank,
            "User Score ": user_score,
            "User Score (Rounded) ": user_score_rounded,
            "User Rating Count ": user_rating_count,
            "Yearly Chart Position (User) ": user_year_placement,
            "All-Time Chart Position (User) ": user_all_time_placement,
            "Year-End Rank (User)" : user_year_end_rank
        }

