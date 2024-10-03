import requests.structures
from .cli import NyfitsaConfig
from .nyfitsa import calculate_percentages, SiteInfos
from typing import Dict

import tyro
import requests

def main():
    config = tyro.cli(NyfitsaConfig)
    websites: Dict[str, SiteInfos] = {}
    for url in config.urls:
        #Délai d'attente de 10 secondes
        response: requests.models.Response = requests.get(url, timeout=10)
        headers: requests.structures.CaseInsensitiveDict[str] = response.headers
        websites[url] = (SiteInfos(url= url, response = response, headers= headers))
    # print(websites[0].headers["server"])
    servers_percentages = calculate_percentages(websites)
    for name, percentage in servers_percentages.items():
        print(f"Nom du serveur: {name} -- valeur: {percentage}%")

if __name__ == "__main__":
    main()