import json
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..primp import Client
from ..utils import asyncify, raise_for_status


@dataclass
class Extension:
    query: str
    description: str
    image: str


@dataclass
class Suggestion:
    t: str  # unknown, may be 'type'
    query: str
    url: str
    ext: Optional[Extension]


def suggest(
    q: Optional[str] = None,
    *,
    market: str = "en-us",
    cookies: Dict[str, str] = {},
) -> List[Suggestion]:
    """Get search suggestions.

    Args:
        q (str, optional): The query to get suggestions for. Default is None.
    """

    client = Client(cookies=cookies, follow_redirects=True, verify=False)
    res = client.get(
        "https://www.bing.com/AS/Suggestions",
        params={
            "pt": "page.home",
            "scope": "web",
            "mkt": market,
            "qry": q or "",
            "cp": "2",
            "csr": "1",
            "msbqf": "false",
            "cvid": uuid.uuid4().hex.upper(),
        },
    )

    raise_for_status(res)
    data = json.loads(res.text)

    return [
        Suggestion(
            t=s["t"],
            query=s["q"].replace("\ue000", "**").replace("\ue001", "*"),
            url=s["u"],
            ext=(
                Extension(
                    query=s["ext"]["t"].replace("\ue000", "**").replace("\ue001", "*"),
                    description=s["ext"]["des"],
                    image=s["ext"]["im"],
                )
                if "ext" in s
                else None
            ),
        )
        for s in data["s"]
    ]


asuggest = asyncify(suggest)
