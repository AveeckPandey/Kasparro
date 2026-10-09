"""Tests for resume parsers and entity extractors."""

import pytest
from src.parsers.entity_extractor import (
    extract_email,
    extract_phone,
    extract_github,
    extract_cgpa,
    extract_candidate_name,
)
from src.parsers.resume_parser import ResumeParser


def test_extract_email():
    text = "Contact me at john.doe@example.com or j_doe99@university.edu"
    assert extract_email(text) == "john.doe@example.com"


def test_extract_github_from_text():
    text = "GitHub: github.com/octocat | Portfolio: octocat.dev"
    url, username = extract_github(text)
    assert url == "https://github.com/octocat"
    assert username == "octocat"


def test_extract_github_from_uri():
    uris = ["https://linkedin.com/in/someone", "https://github.com/developer123"]
    url, username = extract_github("some text", uris)
    assert url == "https://github.com/developer123"
    assert username == "developer123"


def test_extract_cgpa_10_scale():
    text = "Bachelor of Technology in CS, CGPA: 8.75/10"
    val, raw = extract_cgpa(text)
    assert val == 8.75
    assert "8.75/10" in raw


def test_extract_cgpa_4_scale():
    text = "BS in Computer Science | GPA: 3.8 / 4.0"
    val, raw = extract_cgpa(text)
    # 3.8 / 4 * 10 = 9.5
    assert val == 9.5


def test_extract_cgpa_percentage():
    text = "Academic Performance: Aggregate: 82.5%"
    val, raw = extract_cgpa(text)
    # 82.5% -> 8.25
    assert val == 8.25


def test_parser_unreadable_file_tolerance(tmp_path):
    bad_file = tmp_path / "corrupt.pdf"
    bad_file.write_bytes(b"NOT A REAL PDF CONTENT RANDOM BYTES")
    parsed = ResumeParser.parse_file(bad_file)
    assert parsed.parsing_status != "success" or parsed.full_text == ""
