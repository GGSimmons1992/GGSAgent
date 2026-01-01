import pytest
from unittest.mock import patch, Mock

from jobTools.jobFinderTool import JobFinderTool


def make_response(status=200, text=""):
    r = Mock()
    r.status_code = status
    r.text = text
    return r


def test_successful_job_search_returns_links_and_titles():
    # DuckDuckGo HTML search mock with two result links
    search_html = (
        "<html><body>"
        '<a href="http://example.com/job1">Job 1</a>'
        '<a href="/l/?kh=-1&uddg=http%3A%2F%2Fexample.com%2Fjob2">Job 2</a>'
        "</body></html>"
    )

    job1_html = "<html><head><title>Backend Engineer - Example</title></head><body></body></html>"
    job2_html = (
        "<html><head><title>Data Engineer - Example</title></head><body></body></html>"
    )

    def side_effect(url, *args, **kwargs):
        if url.startswith("https://html.duckduckgo.com/html/"):
            return make_response(200, search_html)
        elif url == "http://example.com/job1":
            return make_response(200, job1_html)
        elif url == "http://example.com/job2":
            return make_response(200, job2_html)
        else:
            return make_response(404, "")

    with patch("jobTools.jobFinderTool.requests.get", side_effect=side_effect):
        tool = JobFinderTool()
        out = tool.forward("engineer", "remote")

    assert "Backend Engineer - Example - http://example.com/job1" in out
    assert "Data Engineer - Example - http://example.com/job2" in out


def test_search_non_200_returns_error_message():
    with patch("jobTools.jobFinderTool.requests.get") as mock_get:
        mock_get.return_value = make_response(500, "Server Error")
        tool = JobFinderTool()
        out = tool.forward("engineer", "")

    assert "Search failed: status 500" in out


def test_requests_exception_returns_error_string():
    with patch("jobTools.jobFinderTool.requests.get", side_effect=Exception("network")):
        tool = JobFinderTool()
        out = tool.forward("engineer", "")

    assert out.startswith("Error finding jobs:")
    assert "network" in out
