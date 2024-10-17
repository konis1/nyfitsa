
import requests
from typing import List, Dict
from unittest.mock import patch, MagicMock

from src.nyfitsa.nyfitsa import Results, parralelize_fetching


def test_stats_server_valid():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get') as mock_get:
        # Simuler une réponse avec un code 200 et un en-tête de serveur
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"server": "nginx"}
        mock_get.return_value = mock_response

        stats: Results = parralelize_fetching(urls)

        result: Dict[str, float] = stats.stats_server()
        assert result == {"nginx": 100}


def test_stats_server_valid_timeout():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get', side_effect=requests.exceptions.Timeout):
        stats: Results = parralelize_fetching(urls)
        result: Dict[str, float] = stats.stats_server()

        assert result == {"timeout": 100}


def test_stats_server_valid_connection_error():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get',
               side_effect=requests.exceptions.ConnectionError
               ):
        stats: Results = parralelize_fetching(urls)
        result: Dict[str, float] = stats.stats_server()

        assert result == {"connection_error": 100}


def test_stats_server_valid_http_error():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get', side_effect=requests.exceptions.HTTPError):
        stats: Results = parralelize_fetching(urls)
        result: Dict[str, float] = stats.stats_server()

        assert result == {"http_error": 100}


def test_stats_server_empty_list():
    urls: List[str] = []
    with patch('requests.get') as mock_get:
        # Simuler une réponse avec un code 200 et un en-tête de serveur
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_get.return_value = mock_response

        stats: Results = parralelize_fetching(urls)

        result: Dict[str, float] = stats.stats_server()
        assert result == {}
