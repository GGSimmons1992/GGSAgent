import pytest
from unittest.mock import patch, Mock

from jobTools.linkedinTool import LinkedInTool


def make_response(status=200, text=""):
    r = Mock()
    r.status_code = status
    r.text = text
    return r


def test_successful_linkedin_fetch_returns_title_and_content():
    html = (
        "<html><head><title>John Doe - LinkedIn</title></head>"
        "<body><h1>John Doe</h1><p>Experienced engineer with cloud skills</p></body></html>"
    )

    with patch("jobTools.linkedinTool.requests.get") as mock_get:
        mock_get.return_value = make_response(200, html)
        tool = LinkedInTool()
        out = tool.forward("https://www.linkedin.com/in/johndoe")

    assert "Title: John Doe - LinkedIn" in out
    assert "Experienced engineer with cloud skills" in out


def test_non_200_status_returns_error_message():
    with patch("jobTools.linkedinTool.requests.get") as mock_get:
        mock_get.return_value = make_response(403, "Forbidden")
        tool = LinkedInTool()
        out = tool.forward("https://www.linkedin.com/in/forbidden")

    assert "Failed to fetch" in out
    assert "status 403" in out


def test_requests_exception_is_handled():
    with patch("jobTools.linkedinTool.requests.get", side_effect=Exception("network")):
        tool = LinkedInTool()
        out = tool.forward("https://www.linkedin.com/in/error")

    assert out.startswith("Error fetching LinkedIn profile:")
    assert "network" in out
