"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_api_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_api_dashboard_html():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "<!DOCTYPE html>" in resp.text
    assert "Kasparro Screening System" in resp.text


def test_api_get_results():
    resp = client.get("/results")
    assert resp.status_code == 200
    data = resp.json()
    assert "batch_summary" in data
    assert "ranked_candidates" in data
    assert len(data["ranked_candidates"]) > 0


def test_api_download_csv():
    resp = client.get("/download_csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]


def test_api_download_excel():
    resp = client.get("/download_excel")
    assert resp.status_code == 200
    assert "application/vnd.openxmlformats" in resp.headers["content-type"]


def test_api_download_docx():
    resp = client.get("/download_docx")
    assert resp.status_code == 200
    assert "application/vnd.openxmlformats" in resp.headers["content-type"]
