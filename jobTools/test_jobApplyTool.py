import pytest
from unittest.mock import patch, Mock

from jobTools.jobApplyTool import JobApplyTool


def make_response(status=200, text=""):
    r = Mock()
    r.status_code = status
    r.text = text
    return r


def test_successful_cover_letter_and_instructions():
    html = (
        "<html><head><title>Senior Software Engineer</title></head>"
        "<body><p>We are hiring a Senior Software Engineer.</p>"
        "<p>Responsibilities include backend development and cloud infra.</p>"
        "</body></html>"
    )

    with patch("jobTools.jobApplyTool.requests.get") as mock_get:
        mock_get.return_value = make_response(200, html)
        tool = JobApplyTool()
        result = tool.forward(
            "https://example.com/job/1",
            resume_text="Experienced backend engineer",
            applicant_name="Alice",
        )

    assert "Cover Letter:" in result
    assert "Senior Software Engineer" in result
    assert "Experienced backend engineer" in result
    assert "Alice" in result or "[Your Name]" not in result
    assert "Submit via the application link: https://example.com/job/1" in result


def test_non_200_status_returns_failure_message():
    with patch("jobTools.jobApplyTool.requests.get") as mock_get:
        mock_get.return_value = make_response(404, "Not Found")
        tool = JobApplyTool()
        result = tool.forward("https://example.com/missing")

    assert "Failed to fetch job posting: status 404" in result


def test_requests_exception_is_handled():
    with patch("jobTools.jobApplyTool.requests.get", side_effect=Exception("timeout")):
        tool = JobApplyTool()
        result = tool.forward("https://example.com/timeout")

    assert result.startswith("Error preparing application materials:")
    assert "timeout" in result
