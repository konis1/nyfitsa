
import nyfitsa.nyfitsa
import requests

from unittest.mock import patch, MagicMock
from typing import List, Dict


def test_calculate_percentages_valid():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get') as mock_get:
        # Simuler une réponse avec un code 200 et un en-tête de serveur
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"server": "nginx"}
        mock_get.return_value = mock_response
        
        websites = nyfitsa.nyfitsa.fetch_site_infos(urls)
        result: Dict[str,float] = nyfitsa.nyfitsa.calculate_percentages(websites)
        assert result == {"nginx": 100}

def test_calculate_percentages_no_headers():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        websites: Dict[str, nyfitsa.nyfitsa.SiteInfos] = nyfitsa.nyfitsa.fetch_site_infos(urls)
        result: Dict[str,float] = nyfitsa.nyfitsa.calculate_percentages(websites)

        assert result == {"unavailable": 100}

def test_calclulate_percentages_timeout():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get', side_effect=requests.exceptions.Timeout):
        websites: Dict[str, nyfitsa.nyfitsa.SiteInfos] = nyfitsa.nyfitsa.fetch_site_infos(urls)
        result: Dict[str,float] = nyfitsa.nyfitsa.calculate_percentages(websites)
        assert result == {"timeout": 100}


def test_calclulate_percentages_connection_error():
    urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
    with patch('requests.get', side_effect=requests.exceptions.ConnectionError):
        websites: Dict[str, nyfitsa.nyfitsa.SiteInfos] = nyfitsa.nyfitsa.fetch_site_infos(urls)
        result: Dict[str,float] = nyfitsa.nyfitsa.calculate_percentages(websites)
        assert result == {"errors": 100}