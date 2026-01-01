import pytest
from unittest.mock import patch, Mock

from jobTools.portfolioTool import PortfolioTool


def make_response(status=200, text=""):
    r = Mock()
    r.status_code = status
    r.text = text
    return r


def test_successful_portfolio_fetch_returns_title_meta_and_content():
    html = (
        "<html><head><title>My Portfolio</title>"
        '<meta name="description" content="A portfolio of projects">'
        "</head><body><h1>Projects</h1><p>Project A - a web app</p><li>Project B</li></body></html>"
    )

    with patch("jobTools.portfolioTool.requests.get") as mock_get:
        mock_get.return_value = make_response(200, html)
        tool = PortfolioTool()
        out = tool.forward("https://portfolio.example")

    assert "Title: My Portfolio" in out
    assert "Meta description: A portfolio of projects" in out
    assert "Project A - a web app" in out


def test_non_200_status_returns_failure_message():
    with patch("jobTools.portfolioTool.requests.get") as mock_get:
        mock_get.return_value = make_response(404, "Not Found")
        tool = PortfolioTool()
        out = tool.forward("https://portfolio.example/missing")

    assert "Failed to fetch" in out
    assert "status 404" in out


def test_requests_exception_is_handled():
    with patch("jobTools.portfolioTool.requests.get", side_effect=Exception("network")):
        tool = PortfolioTool()
        out = tool.forward("https://portfolio.example/error")

    assert out.startswith("Error fetching portfolio:")
    assert "network" in out
