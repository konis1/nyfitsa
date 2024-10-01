import requests.structures
from .cli import NyfitsaConfig
from .nyfitsa import get_servers_quantities, calculate_percentages, SiteInfos
from typing import List, Dict

import tyro
import requests

def main():
    config = tyro.cli(NyfitsaConfig)
    websites: List[SiteInfos] = []
    for url in config.urls:
        #Délai d'attente de 10 secondes
        response: requests.models.Response = requests.get(url, timeout=10)
        headers: requests.structures.CaseInsensitiveDict[str] = response.headers
        websites.append(SiteInfos(url= url, response = response, headers= headers))
    print(websites[0].headers["server"])
    # servers = get_servers_quantities(list(set(config.urls))) # Suppression des doublons
    # servers_percentages = calculate_percentages(servers)
    # for name, percentage in servers_percentages.items():
    #     print(f"Nom du serveur: {name} -- valeur: {percentage}%")

if __name__ == "__main__":
    main()