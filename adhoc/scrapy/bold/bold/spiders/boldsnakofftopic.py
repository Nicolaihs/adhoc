from typing import List
import scrapy
import re
from datetime import date


def parse_random_date(date_str: str):
    """
    Parse a date from a random string format using dateutil.

    Args:
        date_str (str): The input string containing the date.

    Returns:
        datetime.datetime: The parsed datetime object.
    """
    months = [
        "januar",
        "februar",
        "marts",
        "april",
        "maj",
        "juni",
        "juli",
        "august",
        "september",
        "oktober",
        "november",
        "december",
    ]
    # Use regest to extract day, month and year of the format "1. januar 2021"
    date_str = date_str.lower()
    regex = rf"(\d\d?)\.? ({'|'.join(months)}) (\d\d\d\d)"
    dates = re.findall(regex, date_str)
    if dates:
        day, month, year = dates[0]

        # Create datetime object
        date_obj = date(int(year), months.index(month) + 1, int(day))
    else:
        date_obj = None
    return date_obj


def handle_date(date_elements: list):
    timestamps = []
    date_strings = []
    for date_element in date_elements:
        date_content = date_element.css("::text").get()
        date_string = date_element.attrib.get("title")
        if date_string:
            timestamp = parse_random_date(date_string)
            if timestamp:
                # Append timestamp as YYYY-MM-DD
                timestamps.append(timestamp.strftime("%Y-%m-%d"))
        date_strings.append(date_string if date_string else date_content)
    return timestamps, date_strings


def create_data(
    date_elements: list,
    titles: list,
    text: List[str],
    type: str,
    author: str,
    url: str,
    topics: list,
) -> dict:
    timestamps, date_strings = handle_date(date_elements)
    timestamp = len(timestamps) > 0 and timestamps[0] or ""
    data = []
    data = {
        "date_string": date_strings,
        "date": timestamp,
        "title": titles,
        "author": author,
        "text": text,
        "parent_url": url,
        "type": type,
        "topics": topics,
    }

    return data


class BoldsnakofftopicSpider(scrapy.Spider):
    name = "boldsnakofftopic"
    allowed_domains = ["bold.dk"]
    start_urls = ["https://bold.dk/snak/off-topic?room_id=4"]
    # start_urls = [
    #     "https://bold.dk/snak/off-topic/erfaringer-med-postnord?room_id=4&thread_id=572368"
    # ]

    custom_settings = {"DOWNLOAD_DELAY": 2}  # n seconds of delay

    def start_requests(self):
        url = getattr(self, "start_url", None)
        if not url:
            url = self.start_urls[0]
        self.topics = getattr(self, "topics", "").split(",")
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        # Main post
        for post in response.css("div.thread-details"):
            date_elements = post.css(
                "div.thread-head div.userinfo div.userinfo-container div.thread-datetime span"
            )
            author = post.css(
                "div.thread-head div.userinfo div.userinfo-container div a.username::text"
            ).get()
            data = create_data(
                url=response.url,
                titles=post.css(
                    "div.thread-head div.userinfo h2.thread-title::text"
                ).getall(),
                text=post.css("div.thread-body div::text").getall(),
                type="post",
                author="Unknown",
                date_elements=date_elements,
                topics=self.topics,
            )
            yield data

        # Replies
        for post in response.css("div.component_post"):
            date_elements = post.css(
                "div.component_post_top div.userinfo-container div.post-datetime span"
            )
            text = post.css("div.post-text div.text::text").getall()
            author = post.css(
                "div.component_post_top div.userinfo-container div a.username::text"
            ).get()
            data = create_data(
                url=response.url,
                titles="## REPLY ##",
                text=text,
                type="reply",
                author=author,
                date_elements=date_elements,
                topics=self.topics,
            )
            yield data

        # Follow links to thread pages
        anchors = response.css("div.components_post_list div.card h4.title a")
        yield from response.follow_all(anchors, callback=self.parse)

        # Go to next page (if next button not disabled)
        next_page = response.css("nav.components_forum_pagination div.form-row a.next")
        next_class = next_page.css("::attr(class)").get()
        if (
            next_page is not None
            and next_class is not None
            and "disabled" not in next_class
        ):
            yield response.follow(
                next_page.css("::attr(href)").get(), callback=self.parse
            )
