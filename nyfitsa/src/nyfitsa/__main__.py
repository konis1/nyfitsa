from .cli import NyfitsaConfig
from .nyfitsa import calculate_percentages, fetch_site_infos

import tyro

def main():
    config = tyro.cli(NyfitsaConfig)
    websites = fetch_site_infos(config.urls)
    headers_percentages = calculate_percentages(websites, config.header)
    for name, percentage in headers_percentages.items():
        print(f"Header: {config.header}, content: {name} -- value: {percentage}%")

if __name__ == "__main__":
    main()