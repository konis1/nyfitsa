import requests
from requests import structures
from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, List

@dataclass
class SiteInfos:
    url: str
    headers: structures.CaseInsensitiveDict[str]
    response: requests.models.Response

# def get_all_servers_quantities(headers: structures.CaseInsensitiveDict[str]) -> Dict[str, int]:
#     """

#     Récupère les noms de serveurs ainsi que le nombre d'occurences de chacun.

#     Cette fonction prend une liste d'urls en argument et retourne un dictionnaire avec le nom du serveur et le nombre d'occurences.

#     Parameters
#     ----------

#     urls: list of str
#         La liste des urls.

#     Returns
#     -------
#     dict of str, int
#         Un dictionnaire donc la clé est le nom du serveur et la valeur le nombre d'occurences.
    
#     """
#     servers: Dict[str, int] = defaultdict(int)

#     #Parcours de chaque url dans la liste d'urls données
#     for url in urls:

#         try:
            
#             if response.status_code == requests.codes.ok:
#                 # Nom du serveur à partir de l'entête ou "unavailable" si l'information n'est pas dans l'entête
#                 server_name: str = response.headers.get("server", "unavailable")

#                 #Incrémentation du compteur pour ce serveur ou "unavailable"
#                 servers[server_name] += 1
#         except requests.exceptions.Timeout:
#             #Incrémentation du compteur si timeout
#             servers["timeout"] += 1
#         except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
#             servers["errors"] += 1
#     return(servers)

def calculate_percentages(websites: List[SiteInfos]):
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
    servers: Dict[str, int] = defaultdict(int)
    servers_percentages: Dict[str, float] = {}
    for website in websites:
        try:
            if website.response.status_code == requests.codes.ok:
                # Nom du serveur à partir de l'entête ou "unavailable" si l'information n'est pas dans l'entête
                server_name: str = website.response.headers.get("server", "unavailable")

                #Incrémentation du compteur pour ce serveur ou "unavailable"
                servers[server_name] += 1
        except requests.exceptions.Timeout:
            #Incrémentation du compteur si timeout
            servers["timeout"] += 1
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            servers["errors"] += 1

    # Nombre total de valeurs
    total: int = sum(servers.values())
    if total == 0:
        return(servers_percentages)
    for server_name, qty in servers.items():
        servers_percentages[server_name] = round((qty/total) * 100, 2)
    return servers_percentages


    
