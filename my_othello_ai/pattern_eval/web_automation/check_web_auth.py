#!/usr/bin/env python3
"""Check whether OTHELLOPY_AUTH_TOKEN works for othellopy.com APIs."""

from __future__ import annotations

import base64
import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def normalize_auth_token(token: str) -> str:
    token = token.strip()
    if token.lower().startswith("bearer "):
        return token[7:].strip()
    return token


def decode_jwt_part(part: str) -> dict:
    padding = "=" * (-len(part) % 4)
    raw = base64.urlsafe_b64decode(part + padding)
    return json.loads(raw.decode("utf-8"))


def print_token_summary(token: str) -> None:
    parts = token.split(".")
    print(f"token parts: {len(parts)}")
    if len(parts) != 3:
        print("token check: not a JWT-like token")
        return

    header = decode_jwt_part(parts[0])
    payload = decode_jwt_part(parts[1])
    print(f"alg: {header.get('alg')}")
    print(f"aud: {payload.get('aud')}")
    print(f"iss: {payload.get('iss')}")
    print(f"email: {payload.get('email')}")

    exp = payload.get("exp")
    if isinstance(exp, int):
        remaining = exp - int(time.time())
        print(f"expires_in_seconds: {remaining}")
        if remaining <= 0:
            print("token check: expired")


def request_players(token: str) -> None:
    request = Request(
        "https://othellopy.com/api/players?includeDefaults=true",
        method="GET",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"api check: HTTP {exc.code} {exc.reason}")
        print(body[:500])
        return
    except URLError as exc:
        print(f"api check: request failed: {exc.reason}")
        return

    print(f"api check: OK HTTP {response.status}")
    print(body[:500])


def main() -> int:
    token = normalize_auth_token(os.environ.get("OTHELLOPY_AUTH_TOKEN", ""))
    if not token:
        print("OTHELLOPY_AUTH_TOKEN is empty")
        return 2
    print_token_summary(token)
    request_players(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
