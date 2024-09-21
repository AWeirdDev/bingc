from dataclasses import dataclass
from typing import Dict, List, Optional

from selectolax.lexbor import LexborHTMLParser as Parser

from ..primp import Client
from ..utils import asyncify, raise_for_status


@dataclass
class NewsCard:
    title: str
    snippet: str
    url: str
    source: str
    timestamp: str
    color: Optional[str]
    image: Optional[str]


@dataclass
class NewsArticle:
    title: str
    snippet: Optional[str]
    url: str
    image: Optional[str]


@dataclass
class NewsLanding:
    headlines: List[NewsCard]
    trending: List[NewsArticle]


def news(
    *,
    region: Optional[str] = None,
    language: Optional[str] = None,
    cookies: Dict[str, str] = {},
) -> NewsLanding:
    """Fetches the latest news from [Bing](https://www.bing.com/news).

    If `region` and `language` are not provided, the default region and language will be determined by Bing.

    Args:
        region (str, optional): The region to fetch news for. For example: `us`.
        language (str, optional): The language to fetch news for. For example: `en`.
    """
    client = Client(cookies=cookies, follow_redirects=True, verify=False)
    res = client.get(
        "https://www.bing.com/news",
        params={"cc": region or "", "setlang": language or ""},
    )
    raise_for_status(res)

    parser = Parser(res.text)

    # Get headlines
    headlines = []

    for card in parser.css("#news-headlines .news-card"):
        title = card.attributes.get("data-title") or ""

        # If the title is empty, rest of the card is like so
        # We'll just skip here
        if not title:
            continue

        snptnode = card.css_first(".news_snpt")
        snippet = snptnode.text(strip=True) if snptnode else ""

        url = card.attributes.get("data-url") or ""
        source = card.attributes.get("data-author") or ""

        # Citations
        cite = card.css_first("cite")

        # definitely: cite
        if cite and cite.css("span"):
            # _, ts
            # ^         source (ignored)
            #    ^^     timestamp
            _, ts = cite.css("span")  # this may fail, timestamps may not be present
            timestamp = ts.text().strip().split(" ")[-1]

        else:
            timestamp = ""

        # Background color for the card
        colornode = card.css_first(".news_fbcard")
        if colornode:
            color = (
                (colornode.attributes.get("style") or "color:#000000;")
                .split(":")[-1]
                .strip()
                .strip(";")
            )
        else:
            color = None

        imagenode = card.css_first("img")
        image = (imagenode.attributes.get("src")) if imagenode else None

        headlines.append(
            NewsCard(
                title=title,
                snippet=snippet,
                url=url,
                source=source,
                timestamp=timestamp,
                color=color,
                image=image,
            )
        )

    # For You page
    # todo!()

    # Trending articles
    trending = []

    for article in parser.css("#nttcrsl .tobitem .tobitem_info"):
        title = article.attributes.get("title") or ""

        # Same as headlines, we'll skip here
        if not title:
            continue

        href = article.attributes.get("href") or ""
        imagenode = article.css_first("img")
        image = (imagenode.attributes.get("src")) if imagenode else None

        trending.append(NewsArticle(title=title, url=href, image=image, snippet=None))

    return NewsLanding(headlines=headlines, trending=trending)


# async impl
anews = asyncify(news)
