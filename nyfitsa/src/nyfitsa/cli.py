from dataclasses import dataclass
from pathlib import Path
from pydantic import HttpUrl
import tyro 
from .nyfitsa import fetch_site_infos

@dataclass
class NyfitsaConfig:
    urls: list[HttpUrl]
    """

    Provide different urls to get the headers data.
    urls should have the format http://www.example.com or https://www.example.com

    """
    
    headers: tuple[str, ...] = ("server",'X-Frame-Options', 'X-Content-Type-Options','Referrer-Policy','X-XSS-Protection')
    """

    Provide the type of header you want the stats

    """
    file: Path|None = None
    """"urls in a file. 1 url by line
    """


def main():
    config = tyro.cli(NyfitsaConfig)
    websites = fetch_site_infos(config.urls)
    print(websites)