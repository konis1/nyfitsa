from dataclasses import dataclass
from pathlib import Path
from pydantic import HttpUrl
import tyro
from.nyfitsa import Results
from .nyfitsa import fetch_site_infos, print_headers_stats

@dataclass
class NyfitsaConfig:
    urls: list[HttpUrl]
    """

    Provide different urls to get the headers data.
    urls should have the format http://www.example.com or https://www.example.com

    """

    server_stats: bool = False
    """

    Option to calculate the server stats from the urls list

    """

    file: Path|None = None
    """"

    urls in a file. 1 url by line

    """


def main():
    config = tyro.cli(NyfitsaConfig)
    websites = fetch_site_infos(config.urls)
    if  config.server_stats:
        stats = Results(site_infos= websites)
        print_headers_stats(stats)
