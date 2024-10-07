from dataclasses import dataclass

@dataclass
class NyfitsaConfig:
    urls: list[str]
    """

    Provide different urls to get the headers data.
    urls should have the format http://www.example.com or https://www.example.com

    """
    headers: tuple[str, ...] = ("server",'X-Frame-Options', 'X-Content-Type-Options','Referrer-Policy','X-XSS-Protection')
    """

    Provide the type of header you want the stats

    """

