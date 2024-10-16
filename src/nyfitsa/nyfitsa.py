from enum import Enum
from pydantic import BaseModel
from requests import Response, structures
from requests.exceptions import Timeout, ConnectionError, HTTPError
from typing import Dict, List, Any, Literal
from collections import defaultdict
import requests
from tqdm import tqdm

class ErrorCode(Enum):
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    HTTP_ERROR = "http_error"


"""

Represents the different information we get from a website/

Attributes:
url(str):The website's url
server(str): The server name
x_frame_options(str): The content of x_frame_options header
referrer_policy(str): The content of referrer policy header
xss_protection(str): The content of xss_protection header
err_vode(ErrorCode | None): The Error code if there is one
_response(Response): The response we get for the url

"""


class SiteInfos(BaseModel):
    url: str
    server: str | None = None
    x_frame_options: str | None = None
    x_content_type_options: str | None = None
    referrer_policy: str | None = None
    xss_protection: str | None = None
    err_code: ErrorCode | None = None
    _response: Response | None = None


# fields are the class SIteInfos attributes except url, err_code and response
# fields = [k for k in SiteInfos.model_fields if k not in
#           ["url", "err_code", "_response"]]

# Literal composed of the different headers
StatType = Literal[
    "server",
    "x_frame_options",
    "x_content_type_options",
    "referrer_policy",
    "xss_protection",
]


"""

A class for calculating and printing statistics for various
HTTP headers obtained from a list of SiteInfos objects.

ttributes
----------
site_infos : List[SiteInfos]
    A list of `SiteInfos` objects, each representing information
    about a specific website, including headers and response status.

Methods
-------
stats_server() -> Dict[str, float]
    Calculates the percentage distribution of different
    server types among the websites.

stats_xss_protection() -> Dict[str, float]
    Calculates the percentage distribution of the
    'X-XSS-Protection' header among the websites.

stats_x_frames_options() -> Dict[str, float]
    Calculates the percentage distribution of the
    'X-Frame-Options' header among the websites.

stats_x_content_type_options() -> Dict[str, float]
    Calculates the percentage distribution of the
    'X-Content-Type-Options' header among the websites.

stats_referrer_policy() -> Dict[str, float]
    Calculates the percentage distribution of the
    'Referrer-Policy' header among the websites.

print_stats(
    stat_type: Literal["server", "xss_protection"] | None = None
    ) -> None
    Prints the statistics for the specified header type, if available.


"""


class Results(BaseModel):
    site_infos: List[SiteInfos]

    def _calculate_stats(self, header: str) -> Dict[str, float]:
        counter: Dict[str, int] = defaultdict(int)

        for site in self.site_infos:
            value = getattr(site, header, None)
            if value is not None and site.err_code is None:
                counter[value] += 1
            elif site.err_code == ErrorCode.TIMEOUT:
                counter["timeout"] += 1
            elif site.err_code == ErrorCode.CONNECTION_ERROR:
                counter["connection_error"] += 1
            elif site.err_code == ErrorCode.HTTP_ERROR:
                counter["http_error"] += 1
            else:
                counter["unavailable"] += 1

        stats: Dict[str, float] = {}
        total: int = sum(counter.values())

        if total > 0:
            for element, qty in counter.items():
                stats[element] = round((qty / total) * 100, 2)

        return stats

    def stats_server(self) -> Dict[str, float]:
        return self._calculate_stats("server")

    def stats_xss_protection(self) -> Dict[str, float]:
        return self._calculate_stats("xss_protection")

    def stats_x_frames_options(self) -> Dict[str, float]:
        return self._calculate_stats("x_frame_options")

    def stats_x_content_type_options(self) -> Dict[str, float]:
        return self._calculate_stats("x_content_type_options")

    def stats_referrer_policy(self) -> Dict[str, float]:
        return self._calculate_stats("referrer_policy")

    def print_stats(
        self,
        stat_type: StatType | None = None
    ) -> None:
        stats: Dict[str, float] | None = None
        # Appeler la méthode en fonction du type de statistique demandé
        if stat_type == "server":
            stats = self.stats_server()
        elif stat_type == "xss_protection":
            stats = self.stats_xss_protection()
        elif stat_type == "x_frame_options":
            stats = self.stats_x_frames_options()
        elif stat_type == "x_content_type_options":
            stats = self.stats_x_content_type_options()
        elif stat_type == "referrer_policy":
            stats = self.stats_referrer_policy()

        # Vérifie si des statistiques existent et les imprime
        if isinstance(stats, dict):
            print(f"{stat_type} stats:")
            for key, percentage in stats.items():
                print(f"- {key}: {percentage}%")
        else:
            print("No stats available")


def fetch_headers(response: Response) -> Dict[str, str]:
    headers: structures.CaseInsensitiveDict[str] = response.headers
    return {
        "server": headers.get("server", "unavailable"),
        "x_frame_options": headers.get("X-Frame-Options", "unavailable"),
        "x_content_type_options": headers.get(
            "X-Content-Type-Options", "unavailable"),
        "referrer_policy": headers.get("Referrer-Policy", "unavailable"),
        "xss_protection": headers.get("X-XSS-Protection", "unavailable"),
    }


def fetch_site_infos(urls: List[str]) -> Results:
    websites: List[Dict[str, Any]] = []
    existing_url: set[str] = set()
    # If url already analyzed then skip
    for url in tqdm(urls, desc="Fetching urls headers", colour="green"):
        if url in existing_url:
            continue

        d: Dict[str, Any] = {"url": url}
        try:
            # Délai d'attente de 10 secondes
            response: Response = requests.get(str(url), timeout=10)
            response.raise_for_status()

            headers: Dict[str, str] = fetch_headers(response)
            existing_url.add(url)
            d |= {
                "server": headers["server"],
                "x_frame_options": headers["x_frame_options"],
                "x_content_type_options": headers["x_content_type_options"],
                "referrer_policy": headers["referrer_policy"],
                "xss_protection": headers["xss_protection"],
                "response": response,
                "err_code": None,
            }

        except Timeout:
            d["err_code"] = ErrorCode.TIMEOUT
            existing_url.add(url)

        except ConnectionError:
            d["err_code"] = ErrorCode.CONNECTION_ERROR
            existing_url.add(url)

        except HTTPError:
            d["err_code"] = ErrorCode.HTTP_ERROR
            existing_url.add(url)

        finally:
            websites.append(d)
    results = Results.model_validate({"site_infos": websites})
    return results
