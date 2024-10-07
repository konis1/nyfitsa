from .cli import NyfitsaConfig
from .nyfitsa import calculate_percentages, fetch_site_infos, print_headers_stats

import tyro

def main():
    config = tyro.cli(NyfitsaConfig)
    websites = fetch_site_infos(config.urls)
    headers_percentages = calculate_percentages(websites, config.headers)
    print_headers_stats(headers_percentages)
    

if __name__ == "__main__":
    main()