import dataclasses
import requests
import tyro

from collections import defaultdict
from typing import List, Dict

def check_valid_url():
    return

def get_servers_quantities(urls: List[str]) -> Dict[str, int]:
    """

    Récupère les noms de serveurs ainsi que le nombre d'occurences de chacun.

    Cette fonction prend une liste d'urls en argument et retourne un dictionnaire avec le nom du serveur et le nombre d'occurences.

    Parameters
    ----------

    urls: list of str
        La liste des urls.

    Returns
    -------
    dict of str, int
        Un dictionnaire donc la clé est le nom du serveur et la valeur le nombre d'occurences.
    
    """
    servers: Dict[str, int] = defaultdict(int)

    #Parcours de chaque url dans la liste d'urls données
    for url in urls:
        try:
            #Délai d'attente de 10 secondes
            request: requests.models.Response = requests.get(url, timeout=10)
            if request.status_code == requests.codes.ok:
                # Nom du serveur à partir de l'entête ou "unavailable" si l'information n'est pas dans l'entête
                server_name: str = request.headers.get("server", "unavailable")

                #Incrémentation du compteur pour ce serveur ou "unavailable"
                servers[server_name] += 1
        except requests.exceptions.Timeout:
            #Incrémentation du compteur si timeout
            servers["timeout"] += 1
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            servers["errors"] += 1
    return(servers)

def calculate_percentages(servers: Dict[str, int]) -> Dict[str, float]:
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
    servers_percentages: Dict[str, float] = {}
    # Nombre total de valeurs
    total: int = sum(servers.values())
    if total == 0:
        return(servers_percentages)
    for server_name, qty in servers.items():
        servers_percentages[server_name] = round((qty/total) * 100, 2)
    return servers_percentages

@dataclasses.dataclass
class nyfitsaConfig:
    urls: list[str]
    """

    Provide different urls to get the stats.
    urls should have the format http://www.example.com or https://www.example.com

    """

if __name__ == "__main__":
    config = tyro.cli(nyfitsaConfig)
    servers = get_servers_quantities(config.urls)
    servers_percentages = calculate_percentages(servers)
    for name, percentage in servers_percentages.items():
        print(f"Nom du serveur: {name} -- valeur: {percentage}%")
    
