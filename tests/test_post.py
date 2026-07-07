from unittest.mock import MagicMock, patch
import pytest
import post


def _mock_resp(json_data: dict) -> MagicMock:
    m = MagicMock()
    m.json.return_value = json_data
    m.raise_for_status.return_value = None
    return m


# --- _create_container ---

def test_create_container_posts_correct_params():
    with patch("post.requests.post") as mock_post:
        mock_post.return_value = _mock_resp({"id": "ctr_abc"})
        result = post._create_container("user99", "https://img/x.png", "caption", "tok123")
        assert result == "ctr_abc"
        _, kwargs = mock_post.call_args
        params = kwargs["params"]
        assert params["image_url"] == "https://img/x.png"
        assert params["caption"] == "caption"
        assert params["access_token"] == "tok123"


# --- _poll_container ---

def test_poll_container_returns_immediately_on_finished():
    with patch("post.requests.get") as mock_get, patch("post.time.sleep") as mock_sleep:
        mock_get.return_value = _mock_resp({"status_code": "FINISHED"})
        post._poll_container("ctr1", "tok")
        mock_sleep.assert_not_called()
        mock_get.assert_called_once()


def test_poll_container_retries_while_in_progress():
    with patch("post.requests.get") as mock_get, patch("post.time.sleep"):
        mock_get.side_effect = [
            _mock_resp({"status_code": "IN_PROGRESS"}),
            _mock_resp({"status_code": "IN_PROGRESS"}),
            _mock_resp({"status_code": "FINISHED"}),
        ]
        post._poll_container("ctr1", "tok", retries=5, delay=0)
        assert mock_get.call_count == 3


def test_poll_container_raises_timeout():
    with patch("post.requests.get") as mock_get, patch("post.time.sleep"):
        mock_get.return_value = _mock_resp({"status_code": "IN_PROGRESS"})
        with pytest.raises(TimeoutError, match="not FINISHED"):
            post._poll_container("ctr1", "tok", retries=3, delay=0)


def test_poll_container_raises_on_error_status():
    with patch("post.requests.get") as mock_get, patch("post.time.sleep"):
        mock_get.return_value = _mock_resp({"status_code": "ERROR"})
        with pytest.raises(RuntimeError, match="ERROR state"):
            post._poll_container("ctr1", "tok")


# --- _publish_container ---

def test_publish_container_returns_media_id():
    with patch("post.requests.post") as mock_post:
        mock_post.return_value = _mock_resp({"id": "media_xyz"})
        result = post._publish_container("user99", "ctr1", "tok123")
        assert result == "media_xyz"
        _, kwargs = mock_post.call_args
        assert kwargs["params"]["creation_id"] == "ctr1"


# --- publish_image (integration) ---

def test_publish_image_calls_all_three_steps():
    with (
        patch("post.requests.post") as mock_post,
        patch("post.requests.get") as mock_get,
        patch("post.time.sleep"),
    ):
        mock_post.side_effect = [
            _mock_resp({"id": "ctr_1"}),
            _mock_resp({"id": "media_final"}),
        ]
        mock_get.return_value = _mock_resp({"status_code": "FINISHED"})
        result = post.publish_image("https://img/x.png", "caption", "user99", "tok123")
        assert result == "media_final"
        assert mock_post.call_count == 2
        mock_get.assert_called_once()
