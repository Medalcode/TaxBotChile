import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dashboard"))

from utils import API_URL, api_delete, api_get, api_post, init_session, require_auth


class MockSessionState(dict):

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None

    def __setattr__(self, name, value):
        self[name] = value


def test_init_session_sets_defaults():
    mock_session = MockSessionState()
    with patch("streamlit.session_state", mock_session):
        init_session()
        assert mock_session.token is None
        assert mock_session.usuario is None


def test_require_auth_stops_when_no_token():
    mock_session = MockSessionState(token=None)
    with (
        patch("streamlit.session_state", mock_session),
        patch("streamlit.warning") as mock_warn,
        patch("streamlit.stop") as mock_stop,
    ):
        require_auth()
        mock_warn.assert_called_once()
        mock_stop.assert_called_once()



def test_api_helpers_headers():
    mock_session = MockSessionState(token="fake_token_123")
    with patch("streamlit.session_state", mock_session):
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200)
            api_get("/test-path")
            mock_get.assert_called_once_with(
                f"{API_URL}/test-path",
                headers={"Authorization": "Bearer fake_token_123"},
                timeout=10,
            )

        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            api_post("/test-path", json={"foo": "bar"})
            mock_post.assert_called_once_with(
                f"{API_URL}/test-path",
                json={"foo": "bar"},
                headers={"Authorization": "Bearer fake_token_123"},
                timeout=10,
            )

        with patch("requests.delete") as mock_delete:
            mock_delete.return_value = MagicMock(status_code=200)
            api_delete("/test-path/1")
            mock_delete.assert_called_once_with(
                f"{API_URL}/test-path/1",
                headers={"Authorization": "Bearer fake_token_123"},
                timeout=10,
            )
