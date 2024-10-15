from enum import Enum
from pydantic import BaseModel
from requests import Response, structures
from requests.exceptions import Timeout, ConnectionError, HTTPError
from typing import Dict, List, Any, Literal
from collections import defaultdict

import requests


class ErrorCode(Enum):
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    HTTP_ERROR = "http_error"


class SiteInfos(BaseModel):
    url: str
    server: str | None = None
    x_frame_options: str | None = None
    x_content_type_options: str | None = None
    referrer_policy: str | None = None
    xss_protection: str | None = None
    err_code: ErrorCode | None = None
    _response: Response | None = None


fields = [k for k in SiteInfos.model_fields if k != "url"]
StatType: Literal | None = Literal[*fields]


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
                stats[element] = round((qty/total) * 100, 2)

        return stats

    def stats_server(self) -> Dict[str, float]:
        return self._calculate_stats("server")

    def stats_xss_protection(self) -> Dict[str, float]:
        return self._calculate_stats("X-XSS-Protection")

    def stats_x_frames_options(self) -> Dict[str, float]:
        return self._calculate_stats("X-Frame-Options")

    def stats_x_content_type_options(self) -> Dict[str, float]:
        return self._calculate_stats("X-Content-Type-Options")

    def stats_referrer_policy(self) -> Dict[str, float]:
        return self._calculate_stats("Referrer-Policy")

    def print_stats(
            self,
            stat_type: Literal[
                "server",
                "xss_protection",
                ] | None = None) -> None:
        stats: Dict[str, float] | None = None
        # Appeler la méthode en fonction du type de statistique demandé
        if stat_type == "server":
            stats = self.stats_server()

        # Vérifie si des statistiques existent et les imprime
        if isinstance(stats, dict):
            print(f"{stat_type} stats:")
            for key, percentage in stats.items():
                print(f"- {key}: {percentage}%")
        else:
            print("No stats available")


def create_site_info(
        url: str,
        server: str | None,
        x_frame_options: str | None,
        x_content_type_options: str | None,
        referrer_policy: str | None,
        xss_protection: str | None,
        response: Response | None,
        err_code: ErrorCode | None = None
        ) -> SiteInfos:
    return SiteInfos(
        url=url,
        server=server,
        x_frame_options=x_frame_options,
        x_content_type_options=x_content_type_options,
        referrer_policy=referrer_policy,
        xss_protection=xss_protection,
        err_code=err_code,
        _response=response
    )


def fetch_headers(response: Response) -> Dict[str, str]:
    headers: structures.CaseInsensitiveDict[str] = response.headers
    return {
        "server": headers.get("server", "unavailable"),
        "x_frame_options": headers.get("X-Frame-Options", "unavailable"),
        "x_content_type_options": headers.get(
            "X-Content-Type-Options", "unavailable"
            ),
        "referrer_policy": headers.get("Referrer-Policy", "unavailable"),
        "xss_protection": headers.get("X-XSS-Protection", "unavailable")
    }


def fetch_site_infos(urls: List[str]) -> Results:
    websites: List[Dict[str, Any]] = []
    existing_url: set[str] = set()
    for url in urls:
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
                "err_code": None
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
