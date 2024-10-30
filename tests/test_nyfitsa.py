
from typing import Dict, Any
from unittest.mock import MagicMock, patch

from src.nyfitsa.nyfitsa import fetch_headers, fetch_single_site_infos
from src.nyfitsa.nyfitsa import SiteInfos, Results, ErrorCode

import requests

from pytest import CaptureFixture

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

    def test_calculate_stats_unavailable(self):

        expected_results: Dict[str, float] = {
            "unavailable": 100.0,
        }

        self.google_site_infos.server = None
        self.wikipedia_site_infos.server = None
        results: Results = Results(site_infos=[
            self.google_site_infos,
            self.wikipedia_site_infos
            ])
        assert results.stats_server() == expected_results


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
    url: str = "http://www.google.com"

    @patch("requests.get")
    def test_fetch_single_site_infos_response_ok(self, mock_get: MagicMock):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Server": "nginx"}
        mock_response.content = b"Success content"
        mock_get.return_value = mock_response

        response = requests.get(self.url, timeout=10)

        assert response.status_code == 200
        assert response.headers["Server"] == "nginx"
        assert response.content == b"Success content"

    @patch("requests.get")
    def test_fetch_single_site_infos_timeout(
            self,
            mock_get: MagicMock
            ):
        mock_get.side_effect = requests.exceptions.Timeout
        # TImeoutException expected
        result = fetch_single_site_infos(self.url)
        expected_result: Dict[str, Any] = {
            "url": self.url,
            "err_code": ErrorCode.TIMEOUT
        }
        assert result == expected_result

    @patch("requests.get")
    def test_fetch_single_site_infos_connection_error(
            self,
            mock_get: MagicMock
            ):
        mock_get.side_effect = requests.exceptions.ConnectionError
        # TImeoutException expected
        result = fetch_single_site_infos(self.url)
        expected_result: Dict[str, Any] = {
            "url": self.url,
            "err_code": ErrorCode.CONNECTION_ERROR
        }
        assert result == expected_result

    @patch("requests.get")
    def test_fetch_single_site_infos_http_error(
            self,
            mock_get: MagicMock
            ):
        mock_get.side_effect = requests.exceptions.HTTPError
        # TImeoutException expected
        result = fetch_single_site_infos(self.url)
        expected_result: Dict[str, Any] = {
            "url": self.url,
            "err_code": ErrorCode.HTTP_ERROR
        }
        assert result == expected_result

    @patch("requests.get")
    def test_fetch_single_site_infos_valid(self, mock_get: MagicMock):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {
            "server": "nginx",
            "X-Frame-Options": "test",
            "X-Content-Type-Options": "test",
            "Referrer-Policy": "test",
            "X-XSS-Protection": "test"
        }
        mock_get.return_value = mock_response

        expected_result: Dict[str, Any] = {
            "url": self.url,
            "server": "nginx",
            "x_frame_options": "test",
            "x_content_type_options": "test",
            "referrer_policy": "test",
            "xss_protection": "test",
            "response": mock_response,
            "err_code": None
        }

        result = fetch_single_site_infos(self.url)
        assert expected_result == result


class TestPrintStats():
    mock_response = MagicMock()

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

    def expected_print(self, stat_type: str, expected_out_value: str) -> str:
        return f"\n==================================================\nStatistics for: {stat_type}\n==================================================\n- {expected_out_value}\n==================================================\n\n"

    def test_print_stats_server(self, capsys: CaptureFixture[str]):
        results: Results = Results(site_infos=[
            self.google_site_infos,
            self.wikipedia_site_infos
            ])
        expected_print: str = self.expected_print("Server", "nginx: 100.00%")
        results.print_stats("server")

        printed: tuple[str, str] = capsys.readouterr()

        assert printed.out == expected_print

    def test_print_xss_protection(self, capsys: CaptureFixture[str]):
        results: Results = Results(site_infos=[
            self.google_site_infos,
            self.wikipedia_site_infos
            ])
        expected_print: str = self.expected_print("Xss Protection", "test: 100.00%")

        results.print_stats("xss_protection")

        printed: tuple[str, str] = capsys.readouterr()

        assert printed.out == expected_print

    def test_print_x_frame_options(self, capsys: CaptureFixture[str]):
        results: Results = Results(site_infos=[
            self.google_site_infos,
            self.wikipedia_site_infos
            ])
        expected_print: str = self.expected_print("X Frame Options", "test: 100.00%")

        results.print_stats("x_frame_options")

        printed: tuple[str, str] = capsys.readouterr()

        assert printed.out == expected_print

    def test_print_x_content_type_options(self, capsys: CaptureFixture[str]):
        results: Results = Results(site_infos=[
            self.google_site_infos,
            self.wikipedia_site_infos
            ])
        expected_print: str = self.expected_print("X Content Type Options", "test: 100.00%")

        results.print_stats("x_content_type_options")

        printed: tuple[str, str] = capsys.readouterr()

        assert printed.out == expected_print

    def test_print_referrer_policy(self, capsys: CaptureFixture[str]):
        results: Results = Results(site_infos=[
            self.google_site_infos,
            self.wikipedia_site_infos
            ])
        expected_print: str = self.expected_print("Referrer Policy", "test: 100.00%")

        results.print_stats("referrer_policy")

        printed: tuple[str, str] = capsys.readouterr()

        assert printed.out == expected_print

    def test_print_no_stats_available(self, capsys: CaptureFixture[str]):
        self.google_site_infos.referrer_policy = None
        results: Results = Results(site_infos=[self.google_site_infos])
        expected_print: str = "\n==================================================\nNo statistics available for: Referrer Polic\n==================================================\n\n"

        results.print_stats("referrer_polic")

        printed: tuple[str, str] = capsys.readouterr()

        assert printed.out == expected_print
