from requests import Response, structures
from requests.exceptions import Timeout, ConnectionError, HTTPError
from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, List

import requests


@dataclass
class SiteInfos:
    url: str
    headers: structures.CaseInsensitiveDict[str] | None
    response: Response | None
    err_code: str = ""

def fetch_site_infos(urls: List[str]) -> Dict[str,SiteInfos]: 
    websites: Dict[str, SiteInfos] = {}
    for url in urls:
        try:
            #Délai d'attente de 10 secondes
            response: Response = requests.get(url, timeout=10)
            response.raise_for_status()

            headers: structures.CaseInsensitiveDict[str] = response.headers
            websites[url] = SiteInfos(url= url, response = response, headers= headers)

        except Timeout:
            websites[url] = SiteInfos(url=url, response=None, headers=None, err_code= "timeout")
            
        except (ConnectionError, HTTPError):
            websites[url] = SiteInfos(url=url, response=None, headers=None, err_code= "errors")
    return websites

def calculate_percentages(websites: Dict[str, SiteInfos], headers: tuple[str, ...]) -> Dict[str, Dict[str, float]]:
    """
    Calculate the percentage of each header content across a list of given websites.

    This function takes a dictionary with a string as a key and `SiteInfos` as the value, 
    along with a list of headers to analyze. It returns a nested dictionary with header names
    as keys and dictionaries of header content percentages.

    Example Output:
    --------------
    {
        "server": {"gws": 50.0, "nginx": 50.0},
        "content-type": {"text/html": 70.0, "application/json": 30.0}
    }

    Parameters
    ----------
    websites: dict of str, SiteInfos
        A dictionary where the key is the URL of the website and the value is the corresponding SiteInfos object.

    headers: tuple of str
        A tuple containing header names to analyze.

    Returns
    -------
    dict of str, dict of str, float
        A dictionary where each key is the name of a header, and each value is another dictionary containing 
        header content as keys and their corresponding percentages as values.
    """
    final_results: Dict[str, Dict[str,float]] = {}

    # Pour chaque header demandé:
    for header_name in headers:
        headers_content_counter: Dict[str, int] = defaultdict(int)

        # Pour chaque site:
        for _, infos in websites.items():
            # Je récupères le header demandé du site si il existe et que le code de réponse est OK
            if infos.response is not None and infos.response.status_code == requests.codes.ok:

                # Contenu du header  ou "unavailable" si l'information n'est pas dans l'entête
                header_content: str = infos.response.headers.get(header_name, "unavailable")

                #Incrémentation du compteur pour ce contenu du header ou "unavailable"
                headers_content_counter[header_content] += 1

            elif infos.err_code == "timeout":
                #Incrémentation du compteur si timeout
                headers_content_counter["timeout"] += 1
            else:
                headers_content_counter["errors"] += 1

        # Je calclule la moyenne: 
        headers_percentages: Dict[str, float] = {}
        total: int = sum(headers_content_counter.values())

        if total > 0:
            for content, qty in headers_content_counter.items():
                headers_percentages[content] = round((qty/total) * 100, 2)
        final_results[header_name] = headers_percentages

    return final_results

def print_headers_stats(headers_stats: Dict[str, Dict[str,float]]):
    """

    Print the headers stats 

    Parameters
    ----------
    header_stats: dict of str as key and dict of str,flaot as value
        A dict with the header name as key and as values the dict with the header content as jey and the percentage as value.
    
    """
    print("-" * 20)
    for header_name, results in headers_stats.items():
        print(f"Header: {header_name}")
        for result_title, result_value in results.items():
            print(f"content: {result_title} -- value: {result_value}%")
        print("-" * 20)