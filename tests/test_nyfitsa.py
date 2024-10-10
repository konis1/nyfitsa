
import requests

from src.nyfitsa import nyfitsa
from unittest.mock import patch, MagicMock
from typing import List, Dict

def test_stats_server_valid():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get') as mock_get:
        # Simuler une réponse avec un code 200 et un en-tête de serveur
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"server": "nginx"}
        mock_get.return_value = mock_response

        websites = nyfitsa.fetch_site_infos(urls)
        stats = nyfitsa.Results(site_infos= websites)

        result: Dict[str,float] = stats.stats_server()
        assert result == {"nginx": 100}

def test_stats_server_with_duplicates():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com", "http://www.google.com"]
    with patch('requests.get') as mock_get:
        # Simuler une réponse avec un code 200 et un en-tête de serveur
        mock_response_google = MagicMock()
        mock_response_google.status_code = 200
        mock_response_google.headers = {"server": "nginx"}
        mock_response_google.raise_for_status = MagicMock()

        mock_response_wikipedia = MagicMock
        mock_response_wikipedia.status_code = 200
        mock_response_wikipedia.headers = {"server": "apache"}
        mock_response_wikipedia.raise_for_status = MagicMock()


        def side_effect(url, timeout=1):
            if "google" in url:
                return mock_response_google
            elif "wikipedia" in url:
                return mock_response_wikipedia

        mock_get.side_effect = side_effect

        websites = nyfitsa.fetch_site_infos(urls)
        stats = nyfitsa.Results(site_infos= websites)

        result: Dict[str,float] = stats.stats_server()
        assert result == {"nginx": 50, "apache": 50}

def test_stats_server_valid_timeout():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get', side_effect=requests.exceptions.Timeout):
        websites: List[nyfitsa.SiteInfos] = nyfitsa.fetch_site_infos(urls)
        stats = nyfitsa.Results(site_infos= websites)
        result: Dict[str,float] = stats.stats_server()

        assert result == {"timeout": 100}

def test_stats_server_valid_connection_error():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get', side_effect=requests.exceptions.ConnectionError):
        websites: List[nyfitsa.SiteInfos] = nyfitsa.fetch_site_infos(urls)
        stats = nyfitsa.Results(site_infos= websites)
        result: Dict[str,float] = stats.stats_server()

        assert result == {"connection_error": 100}

def test_stats_server_valid_http_error():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get', side_effect=requests.exceptions.HTTPError):
        websites: List[nyfitsa.SiteInfos] = nyfitsa.fetch_site_infos(urls)
        stats = nyfitsa.Results(site_infos= websites)
        result: Dict[str,float] = stats.stats_server()

        assert result == {"http_error": 100}

def test_stats_server_empty_list():
    urls: List[str] = []
    with patch('requests.get') as mock_get:
        # Simuler une réponse avec un code 200 et un en-tête de serveur
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_get.return_value = mock_response

        websites = nyfitsa.fetch_site_infos(urls)
        stats = nyfitsa.Results(site_infos= websites)

        result: Dict[str,float] = stats.stats_server()
        assert result == {}

def test_fetch_site_infos_valid():
    pass

def test_fetch_site_infos_http_error():
    pass
def test_fetch_site_infos_connection_error():
    pass
def test_fetch_site_infos_timeout_error():
    pass
def test_fetch_site_infos_other_error():
    pass
