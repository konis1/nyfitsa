from enum import Enum
from pydantic import BaseModel, HttpUrl
from requests import Response, structures
from requests.exceptions import Timeout, ConnectionError, HTTPError
from typing import Dict, List, DefaultDict

import requests


class ErrorCode(Enum):
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    HTTP_ERROR = "http_error"


class SiteInfos(BaseModel):
    url: HttpUrl
    server: str|None
    x_frame_options: str|None
    x_content_type_options: str|None
    referrer_policy: str|None
    xss_protection: str|None
    err_code: ErrorCode|None
    _response: Response|None

class Results(BaseModel):
    site_infos: List[SiteInfos]

    def stats_server(self) -> Dict[str, float]:
        server_counter: Dict[str,int] = DefaultDict(int)
        for site in self.site_infos:
            if site.server is not None and site.err_code is None:
                server_counter[site.server] += 1
            elif site.err_code  == ErrorCode.TIMEOUT:
                server_counter["timeout"] += 1
            elif site.err_code == ErrorCode.CONNECTION_ERROR:
                server_counter["connection_error"] += 1
            elif site.err_code == ErrorCode.HTTP_ERROR:
                server_counter["http_error"] += 1
            else:
                server_counter["unavailable"] += 1

        server_stats: Dict[str, float] = {}
        total: int = sum(server_counter.values())

        if total > 0:
            for server, qty in server_counter.items():
                server_stats[server] = round((qty/total) * 100, 2)

        return server_stats

    def stats_xss_protection(self):
        pass

def create_site_info(url: str, server: str, x_frame_options: str, x_content_type_options: str,
                     referrer_policy: str, xss_protection: str, response: Response, err_code=None) -> SiteInfos:
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

def fetch_headers(response: Response) -> structures.CaseInsensitiveDict:
    headers: structures.CaseInsensitiveDict[str] = response.headers
    return {
        "server": headers.get("server", "unavailable"),
        "x_frame_options": headers.get("X-Frame-Options", "unavailable"),
        "x_content_type_options": headers.get("X-Content-Type-Options", "unavailable"),
        "referrer_policy": headers.get("Referrer-Policy", "unavailable"),
        "xss_protection": headers.get("X-XSS-Protection", "unavailable")
    }

def fetch_site_infos(urls: List[HttpUrl]) -> List[SiteInfos]:
    websites: List[SiteInfos] = []
    for url in urls:
        try:
            #Délai d'attente de 10 secondes
            response: Response = requests.get(str(url), timeout=1)
            response.raise_for_status()

            headers: structures.CaseInsensitiveDict[str] = fetch_headers(response)

            site_infos = create_site_info(
                url=url,
                server=headers["server"],
                x_frame_options=headers["x_frame_options"],
                x_content_type_options=headers["x_content_type_options"],
                referrer_policy=headers["referrer_policy"],
                xss_protection=headers["xss_protection"],
                response=response,
                err_code=None
            )
            websites.append(site_infos)

        except Timeout:
            websites.append(create_site_info(url,None,None,None,None,None,None,ErrorCode.TIMEOUT,))

        except ConnectionError:
            websites.append(create_site_info(url,None,None,None,None,None,None,ErrorCode.CONNECTION_ERROR,))

        except HTTPError:
            websites.append(create_site_info(url,None,None,None,None,None,None,ErrorCode.HTTP_ERROR,))

    return websites

def print_headers_stats(stats: Dict[str, float]):
    """

    Print the headers stats

    Parameters
    ----------
    header_stats: dict of str as key and dict of str,flaot as value
        A dict with the header name as key and as values the dict with the header content as jey and the percentage as value.

    """
    print("-" * 20)
    for header_name, result in stats.items():
        print(f"Header: {header_name}  -- value: {result}%")
        print("-" * 20)
