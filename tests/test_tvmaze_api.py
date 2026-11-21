from unittest.mock import Mock, patch

import pytest

from tvmaze_api import TVMazeError, get_json, image_url, strip_html, year_from_date


def test_strip_html_removes_markup_and_decodes_entities():
    assert strip_html("<p>Tom &amp; Jerry</p>") == "Tom & Jerry"


def test_strip_html_handles_missing_summary():
    assert strip_html(None) == "No summary is available."


def test_year_from_date():
    assert year_from_date("2024-01-15") == "2024"
    assert year_from_date(None) == "—"


def test_image_url_prefers_requested_size_and_falls_back():
    item = {"image": {"medium": "medium.jpg", "original": "original.jpg"}}
    assert image_url(item, "original") == "original.jpg"
    assert image_url(item, "unknown") == "medium.jpg"
    assert image_url({}) is None


@patch("tvmaze_api.build_session")
def test_get_json_sends_params_and_decodes_response(build_session):
    response = Mock(status_code=200)
    response.json.return_value = [{"show": {"name": "Severance"}}]
    response.raise_for_status.return_value = None
    session = build_session.return_value.__enter__.return_value
    session.get.return_value = response

    payload = get_json("search/shows", {"q": "Severance"})

    assert payload[0]["show"]["name"] == "Severance"
    session.get.assert_called_once_with(
        "https://api.tvmaze.com/search/shows",
        params={"q": "Severance"},
        timeout=15,
    )


@patch("tvmaze_api.build_session")
def test_get_json_turns_404_into_friendly_error(build_session):
    response = Mock(status_code=404)
    session = build_session.return_value.__enter__.return_value
    session.get.return_value = response

    with pytest.raises(TVMazeError, match="HTTP 404"):
        get_json("shows/999999999")
