import logging
from base64 import b64encode
from datetime import date, datetime
from typing import List

from yattag import Doc

from exporter.styles import html_style
from qr.qrcoder import QRCoder
from twitterapi.simple_tweet import SimpleTweet


class HTMLExporter:
    def __init__(self, url2qrcode: bool = False) -> None:
        self.logger = logging.getLogger(__name__)
        self.doc = Doc()
        self.url2qrcode = url2qrcode
        self.qrcoder = QRCoder(5, 0)

    def as_string(self, tweets: List[SimpleTweet], title: str, subtitle: str) -> str:
        self.logger.info("Generating HTML...")

        tag = self.doc.tag
        text = self.doc.text

        with tag("html"):
            with tag("head"):
                self.doc.asis(html_style)
            with tag("body"):
                with tag("div", klass="title"):
                    text(title)
                with tag("div", klass="subtitle"):
                    text(subtitle)
                with tag("div", klass="container"):
                    for tweet in tweets:
                        self._tweet2html(tweet)
        html = self.doc.getvalue()

        self.logger.info("HTML generated")
        return html

    def _tweet2html(self, tweet: SimpleTweet) -> None:
        tag = self.doc.tag
        text = self.doc.text

        if self.url2qrcode:
            urls = tweet.extract_urls(remove_http=True)
            tweet.replace_urls("[QR]")

        with tag("div", klass="tweet-box"):
            with tag("div", klass="tweet-content"):
                with tag("div", klass="tweet-text"):
                    with tag("span", klass="tweet-author"):
                        text(f"{tweet.author}: ")
                    text(tweet.text)
                if self.url2qrcode:
                    for url in urls:
                        with tag("div", klass="tweet-qrcode"):
                            inline_svg = self.qrcoder.generate_inline_svg(url)
                            self._inline_svg2data_uri(inline_svg)
            with tag("div", klass="tweet-stats"):
                with tag("div"):
                    text(f"{tweet.created_at} ➥{tweet.retweet_count} ★{tweet.favorite_count}")
                with tag("div"):
                    text(f"@{tweet.uid} id:{tweet.id}")

    def _inline_svg2data_uri(self, inline_svg: str) -> None:
        self.doc.stag("img", src=f"data:image/svg+xml;charset=utf-8;base64,{b64encode(inline_svg).decode()}")