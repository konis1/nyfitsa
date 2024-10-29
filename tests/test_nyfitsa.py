
from typing import Dict
from unittest.mock import MagicMock

from src.nyfitsa.nyfitsa import fetch_headers


class test_FetchHeaders():
    def test_fetch_headers_all_present(self):
        mock_response = MagicMock()
        mock_response.headers = {
            "server": "Nginx",
            "x_frame_options": "DENY",
            "x_content_type_options": "nosniff",
            "referrer_policy": "no-referrer",
            "xss_protection": "1; mode=block",

        }

        expected_results: Dict[str, str] = {
            "server": "Nginx",
            "x_frame_options": "DENY",
            "x_content_type_options": "nosniff",
            "referrer_policy": "no-referrer",
            "xss_protection": "1; mode=block",

        }

        result: Dict[str, str] = fetch_headers(mock_response)

        assert result == expected_results

    def test_fetch_headers_some_present(self):
        mock_response = MagicMock()
        mock_response.headers = {
            "server": "Nginx",
            "x_frame_options": "DENY",

        }

        expected_results: Dict[str, str] = {
            "server": "Nginx",
            "x_frame_options": "DENY",
            "x_content_type_options": "unavailable",
            "referrer_policy": "unavailable",
            "xss_protection": "unavailable",
        }

        result: Dict[str, str] = fetch_headers(mock_response)

        assert result == expected_results

    def test_fetch_headers_none_present(self):
        mock_response = MagicMock()
        mock_response.headers = {

        }

        expected_results: Dict[str, str] = {
            "server": "unavailable",
            "x_frame_options": "unavailable",
            "x_content_type_options": "unavailable",
            "referrer_policy": "unavailable",
            "xss_protection": "unavailable",
        }

        result: Dict[str, str] = fetch_headers(mock_response)

        assert result == expected_results

# def test_stats_server_valid():
#     urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
#     with patch('requests.get') as mock_get:
#         # Simuler une réponse avec un code 200 et un en-tête de serveur
#         mock_response = MagicMock()
#         mock_response.status_code = 200
#         mock_response.headers = {"server": "nginx"}
#         mock_get.return_value = mock_response

#         stats: Results = parralelize_fetching(urls)

#         result: Dict[str, float] = stats.stats_server()
#         assert result == {"nginx": 100}

# Test Parralelize_fetching
# Test fetch single site info
#  Test fetch_site_site_info_Errors

# def test_stats_server_valid_timeout():
#     urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
#     with patch('requests.get', side_effect=requests.exceptions.Timeout):
#         stats: Results = parralelize_fetching(urls)
#         result: Dict[str, float] = stats.stats_server()

#         assert result == {"timeout": 100}


# def test_stats_server_valid_connection_error():
#     urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
#     with patch('requests.get',
#                side_effect=requests.exceptions.ConnectionError
#                ):
#         stats: Results = parralelize_fetching(urls)
#         result: Dict[str, float] = stats.stats_server()

#         assert result == {"connection_error": 100}


# def test_stats_server_valid_http_error():
#     urls: List[str] = ["http://www.google.com", "https://www.wikipedia.com"]
#     with patch('requests.get', side_effect=requests.exceptions.HTTPError):
#         stats: Results = parralelize_fetching(urls)
#         result: Dict[str, float] = stats.stats_server()

#         assert result == {"http_error": 100}


# def test_stats_server_empty_list():
#     urls: List[str] = []
#     with patch('requests.get') as mock_get:
#         # Simuler une réponse avec un code 200 et un en-tête de serveur
#         mock_response = MagicMock()
#         mock_response.status_code = 200
#         mock_response.headers = {}
#         mock_get.return_value = mock_response

#         stats: Results = parralelize_fetching(urls)

#         result: Dict[str, float] = stats.stats_server()
#         assert result == {}
