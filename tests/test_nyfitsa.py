
from typing import Dict
from unittest.mock import MagicMock, patch
import pytest

from src.nyfitsa.nyfitsa import fetch_headers
from src.nyfitsa.nyfitsa import SiteInfos, Results, ErrorCode

import requests


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
        mock_response.headers = {}

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

    def test_calculate_stats_xss_protection(self):

        expected_results: Dict[str, float] = {
            "test": 100.0,
        }

        results: Results = Results(site_infos=[
            self.google_site_infos,
            self.wikipedia_site_infos
            ])
        assert results.stats_xss_protection() == expected_results


class TestResultsErrors():
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
        _response=mock_response,
    )

    wikipedia_site_infos = SiteInfos(
        url="http://www.wikipedia.com",
        _response=mock_response,
    )

    def test_calculate_stats_timeout_error(self):
        self.google_site_infos.err_code = ErrorCode.TIMEOUT
        self.wikipedia_site_infos.err_code = ErrorCode.TIMEOUT

        expected_results: Dict[str, float] = {
            "timeout": 100.0,
        }

        results: Results = Results(site_infos=[
            self.google_site_infos,
            self.wikipedia_site_infos
            ])

        assert results.stats_server() == expected_results
        assert results.stats_x_frames_options() == expected_results
        assert results.stats_x_content_type_options() == expected_results
        assert results.stats_referrer_policy() == expected_results
        assert results.stats_xss_protection() == expected_results

    def test_calculate_stats_connection_error(self):
        self.google_site_infos.err_code = ErrorCode.CONNECTION_ERROR
        self.wikipedia_site_infos.err_code = ErrorCode.CONNECTION_ERROR

        expected_results: Dict[str, float] = {
            "connection_error": 100.0,
        }

        results: Results = Results(site_infos=[
            self.google_site_infos,
            self.wikipedia_site_infos
            ])

        assert results.stats_server() == expected_results
        assert results.stats_x_frames_options() == expected_results
        assert results.stats_x_content_type_options() == expected_results
        assert results.stats_referrer_policy() == expected_results
        assert results.stats_xss_protection() == expected_results

    def test_calculate_stats_http_error(self):
        self.google_site_infos.err_code = ErrorCode.HTTP_ERROR
        self.wikipedia_site_infos.err_code = ErrorCode.HTTP_ERROR

        expected_results: Dict[str, float] = {
            "http_error": 100.0,
        }

        results: Results = Results(site_infos=[
            self.google_site_infos,
            self.wikipedia_site_infos
            ])

        assert results.stats_server() == expected_results
        assert results.stats_x_frames_options() == expected_results
        assert results.stats_x_content_type_options() == expected_results
        assert results.stats_referrer_policy() == expected_results
        assert results.stats_xss_protection() == expected_results


class TestFetchSingleSiteInfos():
    @patch("requests.get")
    def test_fetch_single_site_infos_response_ok(self, mock_get: MagicMock):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Server": "nginx"}
        mock_response.content = b"Success content"
        mock_get.return_value = mock_response

        response = requests.get("http://www.google.com", timeout=10)

        assert response.status_code == 200
        assert response.headers["Server"] == "nginx"
        assert response.content == b"Success content"

    @patch("requests.get")
    def test_fetch_single_site_infos_response_timeout(
            self,
            mock_get: MagicMock
            ):
        mock_get.side_effect = requests.exceptions.Timeout
        # TImeoutException expected
        with pytest.raises(requests.exceptions.Timeout):
            requests.get("http://www.google.com", timeout=10)
