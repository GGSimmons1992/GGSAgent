import pytest
from unittest.mock import patch

from jobTools.resumeTool import ResumeTool


def test_full_resume_parses_name_email_phone_skills_and_experience():
    resume = (
        "John Doe\n"
        "Email: john.doe@example.com\n"
        "Phone: +1 (555) 123-4567\n\n"
        "Skills: Python, AWS, Docker\n\n"
        "Experience:\n"
        "- Backend engineer at Acme Corp\n"
        "- Built scalable APIs\n"
    )

    tool = ResumeTool()
    out = tool.forward(resume)

    assert "Name: John Doe" in out
    assert "Email: john.doe@example.com" in out
    assert "+1 (555) 123-4567" in out
    assert "Top skills: Python, AWS, Docker" in out
    assert "Experience highlights:" in out


def test_empty_resume_returns_not_found_fields():
    tool = ResumeTool()
    out = tool.forward("")

    assert "Name: (not found)" in out
    assert "Email: (not found)" in out
    assert "Phone: (not found)" in out


def test_exception_in_parsing_is_handled():
    with patch("jobTools.resumeTool.re.search", side_effect=Exception("boom")):
        tool = ResumeTool()
        out = tool.forward("anything")

    assert out.startswith("Error parsing resume:")
    assert "boom" in out
