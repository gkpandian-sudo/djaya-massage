# post.py — Meta Graph API v19.0 client
import time

import requests

GRAPH = "https://graph.facebook.com/v19.0"


def _create_container(
    ig_user_id: str, image_url: str, caption: str, access_token: str
) -> str:
    resp = requests.post(
        f"{GRAPH}/{ig_user_id}/media",
        params={
            "image_url": image_url,
            "caption": caption,
            "access_token": access_token,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def _poll_container(
    container_id: str, access_token: str, retries: int = 12, delay: int = 5
) -> None:
    for _ in range(retries):
        resp = requests.get(
            f"{GRAPH}/{container_id}",
            params={"fields": "status_code", "access_token": access_token},
            timeout=30,
        )
        resp.raise_for_status()
        status = resp.json().get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"Container {container_id} entered ERROR state")
        time.sleep(delay)
    raise TimeoutError(f"Container {container_id} not FINISHED after {retries * delay}s")


def _publish_container(ig_user_id: str, container_id: str, access_token: str) -> str:
    resp = requests.post(
        f"{GRAPH}/{ig_user_id}/media_publish",
        params={
            "creation_id": container_id,
            "access_token": access_token,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def publish_image(
    image_url: str, caption: str, ig_user_id: str, access_token: str
) -> str:
    container_id = _create_container(ig_user_id, image_url, caption, access_token)
    _poll_container(container_id, access_token)
    return _publish_container(ig_user_id, container_id, access_token)
