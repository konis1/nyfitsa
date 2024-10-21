from pathlib import Path
from pydantic import BaseModel
import tyro
from .nyfitsa import Results, parralelize_fetching


class NyfitsaConfig(BaseModel):
    urls: list[str] = []
    """

    Provide a list of different urls to get the headers data.
    urls should have the format http://www.example.com
    or https://www.example.com

    """

    stats_server: bool = False
    """

    Activate this option to calculate the server stats from the urls list

    """

    stats_xss_protection: bool = False
    """

    Activate this option to calculate the xss_protection stats from the
    urls list

    """

    stats_x_frame_options: bool = False
    """

    Activate this option to calculate the x_frame_options stats from the
    urls list

    """
    stats_x_content_type_options: bool = False
    """

    Activate this option to calculate the x_content_type_options stats from the
    urls list

    """

    stats_referrer_policy: bool = False
    """

    Activate this option to calculate the referrer policystats from the
    urls list

    """

    file: Path | None = None
    """

    urls in a txt file. 1 url per line

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
    if config.stats_server:
        stats.print_stats("server")
    if config.stats_x_content_type_options:
        stats.print_stats("x_content_type_options")
    if config.stats_x_frame_options:
        stats.print_stats("x_frame_options")
    if config.stats_xss_protection:
        stats.print_stats("xss_protection")
    if config.stats_referrer_policy:
        stats.print_stats("referrer_policy")

    stats.export_stats_to_json()
