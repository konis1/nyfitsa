
import requests

from unittest.mock import patch, MagicMock
from src.nyfitsa import get_servers_quantities
from typing import List, Dict


def test_get_server_quantities_valid():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get') as mock_get:
        # Simuler une réponse avec un code 200 et un en-tête de serveur
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"server": "nginx"}
        mock_get.return_value = mock_response
        
        result: Dict[str,int] = get_servers_quantities(urls)
        assert result == {"nginx": 2}

def test_get_server_quantities_no_headers():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        result: Dict[str,int] = get_servers_quantities(urls)
        assert result == {"unavailable": 2}

def test_get_server_quantities_timeout():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get', side_effect=requests.exceptions.Timeout):
        result: Dict[str,int] = get_servers_quantities(urls)
        assert result == {"timeout": 2}