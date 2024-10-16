from pathlib import Path
from pydantic import BaseModel
import tyro
from .nyfitsa import Results
from .nyfitsa import parralelize_fetching


class NyfitsaConfig(BaseModel):
    urls: list[str] = []
    """

    Provide a list of different urls to get the headers data.
    urls should have the format http://www.example.com
    or https://www.example.com

    """

    server_stats: bool = False
    """

    Activate this option to calculate the server stats from the urls list

    """

    file: Path | None = None
    """"

    urls in a txt file. 1 url by line

    """


def main():
    config = tyro.cli(NyfitsaConfig)
    if config.file is not None:
        # Open file
        config.urls = []
        with open(config.file, "r") as file:
            # Put each url / line in a list
            for line in file:
                config.urls.append(line.strip())
    stats: Results = parralelize_fetching(config.urls)
    if config.server_stats:
        stats.print_stats("server")
