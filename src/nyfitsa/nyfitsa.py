from collections import defaultdict
from enum import Enum
from typing import Dict, List, Any, Literal, Tuple
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
    server_version: str | None = None
    x_frame_options: str | None = None
    x_content_type_options: str | None = None
    referrer_policy: str | None = None
    xss_protection: str | None = None
    err_code: ErrorCode | None = None
    _response: Response | None = None


StatType = Literal[
    "server",
    "server_version",
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

    def _calculate_server_stats(self) -> Tuple[
            Dict[str, float], Dict[str, Dict[str, float]]
            ]:
        counter: Dict[str, int] = defaultdict(int)
        server_version_counter: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
            )

        for site in self.site_infos:
            server_value = getattr(site, "server", None)
            server_version_value = getattr(site, "server_version")
            if (
                server_value is not None
                and site.err_code is None
                and server_value != "unavailable"
            ):
                counter[server_value] += 1
                server_version_counter[server_value][server_version_value] += 1
            else:
                error_key = self._get_error_key(site.err_code)
                counter[error_key] += 1

        stats: Dict[str, float] = self._caclulate_percentage(counter)
        stats = dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))

        server_version_stats: Dict[str, Dict[str, float]] = {}
        for server_type, versions in server_version_counter.items():
            total_versions: int = sum(versions.values())
            server_version_stats[server_type] = {
                version: round((qty / total_versions) * 100, 2)
                for version, qty in versions.items()
            }

        return stats, server_version_stats

    def _caclulate_percentage(
            self, counter: Dict[str, int]
            ) -> Dict[str, float]:
        total: int = sum(counter.values())
        if total == 0:
            return {}
        return {
            key: round((qty / total) * 100, 2) for key, qty in counter.items()
        }

    def _get_error_key(self, err_code: ErrorCode | None) -> str:
        if err_code is None:
            return "unavailable"

        error_map: Dict[ErrorCode, str] = {
            ErrorCode.TIMEOUT: "timeout",
            ErrorCode.CONNECTION_ERROR: "connection_error",
            ErrorCode.HTTP_ERROR: "http_error",
        }
        return error_map.get(err_code, "unavailable")

    def _calculate_stats(self, header: str) -> Dict[str, float]:
        counter: Dict[str, int] = defaultdict(int)

        for site in self.site_infos:
            value = getattr(site, header, None)
            if value is not None and site.err_code is None:
                counter[value] += 1
            else:
                error_key = self._get_error_key(site.err_code)
                counter[error_key] += 1

        stats: Dict[str, float] = self._caclulate_percentage(counter)
        stats = dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))

        return stats

    def stats_server(self) -> Tuple[
            Dict[str, float], Dict[str, Dict[str, float]]
            ]:
        return self._calculate_server_stats()

    def stats_server_version(self) -> Dict[str, float]:
        return self._calculate_stats("server_version")

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
        server_version_stats: Dict[str, Dict[str, float]] | None = None
        # Handle case where no `stat_type` is provided
        if not stat_type:
            print("No statistic type was provided.")
            return

        # Appeler la méthode en fonction du type de statistique demandé
        if stat_type == "server":
            stats, server_version_stats = self.stats_server()
        elif stat_type == "server_version":
            stats = self.stats_server_version()
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
                if server_version_stats is not None and\
                        key in server_version_stats:
                    for version, version_percentage in \
                            server_version_stats[key].items():
                        print(
                            f"  - {version}: {version_percentage:.2f}%"
                            )

            print("="*50 + "\n")
        else:
            print("\n" + "="*50)
            print(
                f"No statistics available for: "
                f"{stat_type.replace('_', ' ').title()}"
                )
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
            "server": get_server_version(headers["server"]),
            "server_version": get_server_version_number(headers["server"]),
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


def get_server_version_number(server_header: str) -> str:
    version_number: List[str] = server_header.split("/")
    if len(version_number) > 1:
        version_number = version_number[-1].split()
        version_number_clean: str = version_number[0].strip("()")
        return version_number_clean
    return "No server version"


def get_server_version(server_header: str) -> str:
    server: List[str] = server_header.split("/")
    if len(server) > 1:
        server = server[0].split()
        server_clean: str = server[0].strip("()")
        return server_clean
    return server_header
