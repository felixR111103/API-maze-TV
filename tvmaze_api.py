"""Small, reusable client for the public TVMaze REST API."""

from __future__ import annotations

import html
import re
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = "https://api.tvmaze.com"


class TVMazeError(RuntimeError):
    """Raised when TVMaze cannot fulfil an API request."""


def build_session() -> requests.Session:
    """Create a session that reuses connections and retries temporary failures."""
    retry = Retry(
        total=3,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "User-Agent": "API-TV-App/1.0 (Applied Programming and AI class project)",
        }
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def get_json(path: str, params: dict[str, Any] | None = None) -> Any:
    """GET one TVMaze resource and return decoded JSON."""
    url = f"{BASE_URL}/{path.lstrip('/')}"
    try:
        with build_session() as session:
            response = session.get(url, params=params, timeout=15)
    except requests.RequestException as exc:
        raise TVMazeError("TVMaze could not be reached. Check your connection.") from exc

    if response.status_code == 404:
        raise TVMazeError("TVMaze did not find a matching resource (HTTP 404).")
    if response.status_code == 429:
        raise TVMazeError("The API rate limit was reached. Wait a few seconds and retry.")
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise TVMazeError(f"TVMaze returned HTTP {response.status_code}.") from exc

    try:
        return response.json()
    except requests.JSONDecodeError as exc:
        raise TVMazeError("TVMaze returned an invalid JSON response.") from exc


def strip_html(value: str | None) -> str:
    """Convert the small HTML fragments returned in summaries to plain text."""
    if not value:
        return "No summary is available."
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def year_from_date(value: str | None) -> str:
    return value[:4] if value else "—"


def image_url(item: dict[str, Any], size: str = "medium") -> str | None:
    image = item.get("image") or {}
    return image.get(size) or image.get("medium") or image.get("original")
