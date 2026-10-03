"""Regression tests for SofaScore.sofascore_request's block-detection logic.

Unlike LanusStats/test_*.py (gitignored, live-network manual scripts), this
file is committed: it uses mocks, needs no network, and pins down the fix for
the most important finding from the curl_cffi migration's final review — a
403/429 whose body is not JSON (e.g. an HTML page from an upstream WAF/CDN)
must raise SofaScoreConnectionError, not a raw ValueError.

Run with: python -m pytest LanusStats/sofascore_regression_test.py -v
"""
from unittest.mock import MagicMock
import pytest

from LanusStats import SofaScore
from LanusStats.exceptions import SofaScoreConnectionError


def _ss_with_fake_response(status_code, text, json_return=None, json_side_effect=None):
    ss = SofaScore()
    fake_response = MagicMock()
    fake_response.status_code = status_code
    fake_response.text = text
    if json_side_effect is not None:
        fake_response.json.side_effect = json_side_effect
    else:
        fake_response.json.return_value = json_return
    fake_session = MagicMock()
    fake_session.get.return_value = fake_response
    ss._session = fake_session
    return ss


def test_non_json_403_body_raises_sofascore_connection_error():
    ss = _ss_with_fake_response(
        403, "<html>Access denied by WAF</html>",
        json_side_effect=ValueError("Expecting value: line 1 column 1")
    )
    with pytest.raises(SofaScoreConnectionError):
        ss.sofascore_request('api/v1/event/123')


def test_json_403_body_still_raises_sofascore_connection_error():
    ss = _ss_with_fake_response(
        403, '{"error": {"code": 403, "reason": "challenge"}}',
        json_return={"error": {"code": 403, "reason": "challenge"}}
    )
    with pytest.raises(SofaScoreConnectionError):
        ss.sofascore_request('api/v1/event/123')


def test_legit_404_still_returns_dict_not_exception():
    ss = _ss_with_fake_response(
        404, '{"error": {"code": 404, "message": "Not Found"}}',
        json_return={"error": {"code": 404, "message": "Not Found"}}
    )
    result = ss.sofascore_request('api/v1/event/123/player/456/rating-breakdown')
    assert result == {"error": {"code": 404, "message": "Not Found"}}
