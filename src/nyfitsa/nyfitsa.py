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


def fetch_site_infos(urls: List[HttpUrl]) -> List[SiteInfos]:
    websites: List[SiteInfos] = []
    for url in urls:
        try:
            #Délai d'attente de 10 secondes
            response: Response = requests.get(str(url), timeout=1)
            response.raise_for_status()

            headers: structures.CaseInsensitiveDict[str] = response.headers
            server: str = headers.get("server", "unavailable")
            x_frame_options: str = headers.get("X-Frame-Options", "unavailable")
            x_content_type_options: str = headers.get("X-Content-Type-Options", "unavailable")
            referrer_policy: str = headers.get("Referrer-Policy", "unavailable")
            xss_protection: str = headers.get("X-XSS-Protection", "unavailable")
            websites.append(
                SiteInfos(
                    url= url,
                    server= server,
                    x_frame_options= x_frame_options,
                    x_content_type_options= x_content_type_options,
                    referrer_policy= referrer_policy,
                    xss_protection= xss_protection,
                    err_code= None,
                    _response = response
                )
            )

        except Timeout:
            websites.append(
                SiteInfos(
                    url= url,
                    server= None,
                    x_frame_options= None,
                    x_content_type_options= None,
                    referrer_policy= None,
                    xss_protection= None,
                    err_code= ErrorCode.TIMEOUT,
                    _response = None
                )
            )

        except ConnectionError:
            websites.append(
                SiteInfos(
                    url= url,
                    server= None,
                    x_frame_options= None,
                    x_content_type_options= None,
                    referrer_policy= None,
                    xss_protection= None,
                    err_code= ErrorCode.CONNECTION_ERROR,
                    _response = None
                )
            )

        except HTTPError:
            websites.append(
                SiteInfos(
                    url= url,
                    server= None,
                    x_frame_options= None,
                    x_content_type_options= None,
                    referrer_policy= None,
                    xss_protection= None,
                    err_code= ErrorCode.HTTP_ERROR,
                    _response = None
                )
            )

    return websites

# output = fetch_site_infos()
# output.stats_server()

# def calculate_percentages(websites: Dict[str, SiteInfos], headers: tuple[str, ...]) -> Dict[str, Dict[str, float]]:
#     """
#     Calculate the percentage of each header content across a list of given websites.

#     This function takes a dictionary with a string as a key and `SiteInfos` as the value,
#     along with a list of headers to analyze. It returns a nested dictionary with header names
#     as keys and dictionaries of header content percentages.

#     Example Output:
#     --------------
#     {
#         "server": {"gws": 50.0, "nginx": 50.0},
#         "content-type": {"text/html": 70.0, "application/json": 30.0}
#     }

#     Parameters
#     ----------
#     websites: dict of str, SiteInfos
#         A dictionary where the key is the URL of the website and the value is the corresponding SiteInfos object.

#     headers: tuple of str
#         A tuple containing header names to analyze.

#     Returns
#     -------
#     dict of str, dict of str, float
#         A dictionary where each key is the name of a header, and each value is another dictionary containing
#         header content as keys and their corresponding percentages as values.
#     """
#     final_results: Dict[str, Dict[str,float]] = {}

#     # Pour chaque header demandé:
#     for header_name in headers:
#         headers_content_counter: Dict[str, int] = defaultdict(int)

#         # Pour chaque site:
#         for _, infos in websites.items():
#             # Je récupères le header demandé du site si il existe et que le code de réponse est OK
#             if infos.response is not None and infos.response.status_code == requests.codes.ok:

#                 # Contenu du header  ou "unavailable" si l'information n'est pas dans l'entête
#                 header_content: str = infos.response.headers.get(header_name, "unavailable")

#                 #Incrémentation du compteur pour ce contenu du header ou "unavailable"
#                 headers_content_counter[header_content] += 1

#             elif infos.err_code == "timeout":
#                 #Incrémentation du compteur si timeout
#                 headers_content_counter["timeout"] += 1
#             else:
#                 headers_content_counter["errors"] += 1

#         # Je calclule la moyenne:
#         headers_percentages: Dict[str, float] = {}
#         total: int = sum(headers_content_counter.values())

#         if total > 0:
#             for content, qty in headers_content_counter.items():
#                 headers_percentages[content] = round((qty/total) * 100, 2)
#         final_results[header_name] = headers_percentages

#     return final_results

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
