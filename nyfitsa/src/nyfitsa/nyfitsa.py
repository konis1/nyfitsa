import requests
# NE fonctionne pas si uniquement requests: question
from requests import structures
from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, List


@dataclass
class SiteInfos:
    url: str
    headers: structures.CaseInsensitiveDict[str] | None
    response: requests.models.Response | None

def fetch_site_infos(urls: List[str]) -> Dict[str,SiteInfos]: 
    websites: Dict[str, SiteInfos] = {}
    for url in urls:
        try:
        #Délai d'attente de 10 secondes
            response: requests.models.Response = requests.get(url, timeout=10)
            headers: structures.CaseInsensitiveDict[str] = response.headers
            websites[url] = SiteInfos(url= url, response = response, headers= headers)
        except requests.exceptions.Timeout:
            websites[url] = SiteInfos(url=url, response=None, headers=None)
    return websites

def calculate_percentages(websites: Dict[str, SiteInfos], header: str = "server"):
    """
    Calcul la quantité d'utilisation d'un serveur en pourcentage.

    Cette fonction prend un dictionnaire avec une string en clé et un int en valeur puis retourne un dictionnaire avec les noms des serveurs en clés et le pourcentage en valeur.  

    Parameters
    ----------
    servers: dict of str, int
        Un dictionnaire donc la clé est le nom du serveur et la valeur le nombre d'occurences.

    Returns
    -------

    dict of str, float
        Un dictionnaire donc la clé est le nom du serveur et la valeur le nombre d'occurences par rapport aux nombre total, en pourcentage.

    """
    headers: Dict[str, int] = defaultdict(int)
    headers_percentages: Dict[str, float] = {}
    for _, infos in websites.items():
        try:
            if infos.response is not None and infos.response.status_code == requests.codes.ok:
                # Nom du serveur à partir de l'entête ou "unavailable" si l'information n'est pas dans l'entête
                header_name: str = infos.response.headers.get(header, "unavailable")

                #Incrémentation du compteur pour ce serveur ou "unavailable"
                headers[header_name] += 1
        except requests.exceptions.Timeout:
            #Incrémentation du compteur si timeout
            headers["timeout"] += 1
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            headers["errors"] += 1

    # Nombre total de valeurs
    total: int = sum(headers.values())
    if total == 0:
        return(headers_percentages)
    for server_name, qty in headers.items():
        headers_percentages[server_name] = round((qty/total) * 100, 2)
    return headers_percentages


    
