
from typing import Dict
from unittest.mock import MagicMock

from src.nyfitsa.nyfitsa import fetch_headers
from src.nyfitsa.nyfitsa import SiteInfos, Results, ErrorCode


class Test_FetchHeaders():
    def test_fetch_headers_all_present(self):
        mock_response = MagicMock()
        mock_response.headers = {
            "server": "Nginx",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer",
            "X-XSS-Protection": "1; mode=block",

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
            "X-Frame-Options": "DENY",

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


class TestResults():

    mock_response = MagicMock()
    mock_response.headers = {
        "Server": "nginx",
        "X-Frame-Options": "test",
        "X-Content-Type-Options": "test",
        "Referrer-Policy": "test",
        "X-XSS-Protection": "test",
    }

    google_site_infos = SiteInfos(
        url="http://www.google.com",
        server="nginx",
        x_frame_options="test",
        x_content_type_options="test",
        referrer_policy="test",
        xss_protection="test",
        _response=mock_response,
    )

    wikipedia_site_infos = SiteInfos(
        url="http://www.wikipedia.com",
        server="nginx",
        x_frame_options="test",
        x_content_type_options="test",
        referrer_policy="test",
        xss_protection="test",
        _response=mock_response,
    )

    def test_calculate_stats_valid(self):

        expected_results: Dict[str, float] = {
            "nginx": 100.0,
        }

        results: Results = Results(site_infos=[
            self.google_site_infos,
            self.wikipedia_site_infos
            ])
        assert results.stats_server() == expected_results
        assert results.stats_x_frames_options() == {"test": 100.0}
        assert results.stats_x_content_type_options() == {"test": 100.0}
        assert results.stats_referrer_policy() == {"test": 100.0}
        assert results.stats_xss_protection() == {"test": 100.0}

    def test_calculate_stats_timeout_error(self):
        mock_response = MagicMock()
        mock_response.headers = {
            "Server": None,
            "X-Frame-Options": None,
            "X-Content-Type-Options": None,
            "Referrer-Policy": None,
            "X-XSS-Protection": None,
            "err_code": "timeout"
        }

        google_site_infos = SiteInfos(
            url="http://www.google.com",
            server=None,
            x_frame_options=None,
            x_content_type_options=None,
            referrer_policy=None,
            xss_protection=None,
            err_code=ErrorCode.TIMEOUT,
            _response=mock_response,
        )

        wikipedia_site_infos = SiteInfos(
            url="http://www.wikipedia.com",
            server=None,
            x_frame_options=None,
            x_content_type_options=None,
            referrer_policy=None,
            xss_protection=None,
            err_code=ErrorCode.TIMEOUT,
            _response=mock_response,
        )

        expected_results: Dict[str, float] = {
            "timeout": 100.0,
        }

        results: Results = Results(site_infos=[
            google_site_infos,
            wikipedia_site_infos
            ])
        assert results.stats_server() == expected_results
        assert results.stats_x_frames_options() == expected_results
        assert results.stats_x_content_type_options() == expected_results
        assert results.stats_referrer_policy() == expected_results
        assert results.stats_xss_protection() == expected_results


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
