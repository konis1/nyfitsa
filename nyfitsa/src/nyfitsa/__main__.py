from .cli import NyfitsaConfig
from .nyfitsa import calculate_percentages, fetch_site_infos

import tyro

def main():
    config = tyro.cli(NyfitsaConfig)
    websites = fetch_site_infos(config.urls)
    servers_percentages = calculate_percentages(websites)
    for name, percentage in servers_percentages.items():
        print(f"Nom du serveur: {name} -- valeur: {percentage}%")

if __name__ == "__main__":
    main()