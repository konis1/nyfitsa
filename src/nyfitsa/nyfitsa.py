from collections import defaultdict
from enum import Enum
from typing import Dict, List, Any, Literal
import os

from pydantic import BaseModel
import multiprocessing
import requests
from requests import Response, structures
from requests.exceptions import Timeout, ConnectionError, HTTPError
from tqdm import tqdm


class ErrorCode(Enum):
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    HTTP_ERROR = "http_error"


class SiteInfos(BaseModel):
    """
        Represents the different information obtained from a website.

        Attributes
        ----------
        url : str
            The website's URL.
        server : Optional[str]
            The server name.
        x_frame_options : Optional[str]
            The content of the X-Frame-Options header.
        x_content_type_options : Optional[str]
            The content of the X-Content-Type-Options header.
        referrer_policy : Optional[str]
            The content of the Referrer-Policy header.
        xss_protection : Optional[str]
            The content of the X-XSS-Protection header.
        err_code : Optional[ErrorCode]
            The error code if there was an issue retrieving the website.
        _response : Optional[Response]
            The response object obtained for the URL.
    """
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


class Results(BaseModel):
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
        stats = dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))

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

        # Handle case where no `stat_type` is provided
        if not stat_type:
            print("No statistic type was provided.")
            return

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
        else:
            stats = None

        # Vérifie si des statistiques existent et les imprime
        if stats is not None:
            print("\n" + "="*50)
            print(f"Statistics for: {stat_type.replace('_', ' ').title()}")
            print("="*50)
            for key, percentage in stats.items():
                print(f"- {key}: {percentage:.2f}%")
            print("="*50 + "\n")
        else:
            print("\n" + "="*50)
            print(f"No statistics available for: \
                {stat_type.replace('_', ' ').title()}")
            print("="*50 + "\n")

    def to_json(self, filename: str = "stats.json"):
        with open(filename, 'w') as f:
            f.write(self.model_dump_json())


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


def parralelize_fetching(urls: List[str]) -> Results:
    websites: List[Dict[str, Any]] = []
    workers: int | None = min(os.cpu_count() or 1, 8)

    with multiprocessing.Pool(workers) as pool:
        for site_info in tqdm(
            pool.imap_unordered(
                fetch_single_site_infos,
                urls
                ),
            total=len(urls),
            desc="Getting sites infos",
            colour="green"
        ):
            websites.append(site_info)
    results = Results.model_validate({"site_infos": websites})
    return results


def fetch_single_site_infos(url: str) -> Dict[str, Any]:
    d: Dict[str, Any] = {"url": url}
    try:
        # Délai d'attente de 10 secondes
        response: Response = requests.get(str(url), timeout=10)
        response.raise_for_status()

        headers: Dict[str, str] = fetch_headers(response)
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

    except ConnectionError:
        d["err_code"] = ErrorCode.CONNECTION_ERROR

    except HTTPError:
        d["err_code"] = ErrorCode.HTTP_ERROR

    return d


def get_server_version_number(server_header: str):
    version_number: List[str] = server_header.split("/")
    return version_number
