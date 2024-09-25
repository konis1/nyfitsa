import requests

from collections import defaultdict
from typing import List, Dict

urls: List[str] = [
    "https://www.wikipedia.org",
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.amazon.com",
    "https://www.twitter.com",
    "https://www.instagram.com",
    "https://www.linkedin.com",
    "https://www.reddit.com",
    "https://www.netflix.com",
    "https://www.microsoft.com",
    "https://www.apple.com",
    "https://www.bbc.com",
    "https://www.cnn.com",
    "https://www.bloomberg.com",
    "https://www.github.com",
    "https://www.medium.com",
    "https://www.stackoverflow.com",
    "https://www.quora.com",
    "https://www.nytimes.com",
    "https://www.washingtonpost.com",
    "https://www.forbes.com",
    "https://www.ted.com",
    "https://www.coursera.org",
    "https://www.edx.org",
    "https://www.udemy.com",
    "https://www.khanacademy.org",
    "https://www.nationalgeographic.com",
    "https://www.spotify.com",
    "https://www.dropbox.com",
    "https://www.slack.com",
    "https://www.zoom.us",
    "https://www.adobe.com",
    "https://www.airbnb.com",
    "https://www.booking.com",
    "https://www.expedia.com",
    "https://www.tripadvisor.com",
    "https://www.paypal.com",
    "https://www.etsy.com",
    "https://www.shopify.com",
    "https://www.walmart.com",
    "https://www.target.com",
    "https://www.imdb.com",
    "https://www.pinterest.com",
    "https://www.flickr.com",
    "https://www.soundcloud.com",
    "https://www.hulu.com",
    "https://www.reuters.com",
    "https://www.aljazeera.com",
    "https://www.theguardian.com"
    ]

def check_valid_url():
    return

def get_servers_quantities(urls: List[str]) -> Dict[str, int]:
    servers: Dict[str, int] = defaultdict(int)
    servers["no_response"] = 0

    #Parcours de chaque url dans la liste d'urls données
    for url in urls:
        try:
            #Délai d'attente de 10 secondes
            request: requests.models.Response = requests.get(url, timeout=10)
            if request.status_code == requests.codes.ok:
                # Nom du serveur à partir de l'entête ou "unavailable" si l'information n'est pas dans l'entête
                server_name: str = request.headers.get("server", "unavailable")

                #Incrémentation du compteur pour ce serveur ou "unavailable"
                servers[server_name] += 1
        except requests.exceptions.RequestException:
            #Incrémentation du compteur si timeout
            servers["no_response"] += 1
    return(servers)

def calculate_percentages(servers: Dict[str, int]) -> Dict[str, float]:
    servers_percentages: Dict[str, float] = {}
    # Nombre total de valeurs
    total: int = sum(servers.values())
    if total == 0:
        return(servers_percentages)
    for server_name, qty in servers.items():
        servers_percentages[server_name] = round((qty/total) * 100, 2)
    return servers_percentages

if __name__ == "__main__":
    servers = get_servers_quantities(urls)
    servers_percentages = calculate_percentages(servers)
    for name, percentage in servers_percentages.items():
        print(f"Nom du serveur: {name} -- valeur: {percentage}%\n")
