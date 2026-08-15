#!/usr/bin/env python3
"""Create othellopy.com matches with TA_Player_v2.

This script does not log in by password. Pass a short-lived Firebase ID token
through OTHELLOPY_AUTH_TOKEN.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


TA_PLAYER_V2_ID = "qZ61Xg3cdvQevP66EEVq"
DEFAULT_BASE_URL = "https://othellopy.com"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create Web-system matches against TA_Player_v2."
    )
    parser.add_argument("--my-player-id", required=True, help="Your submitted Web player ID.")
    parser.add_argument("--games", type=int, default=2, help="Number of matches to create.")
    parser.add_argument(
        "--start-color",
        choices=("black", "white"),
        default="black",
        help="Your color in the first match. Colors alternate after that.",
    )
    parser.add_argument(
        "--opponent-id",
        default=TA_PLAYER_V2_ID,
        help="Opponent Web player ID. Default is TA_Player_v2.",
    )
    parser.add_argument(
        "--my-source",
        choices=("own", "direct", "default"),
        default="own",
        help="Source for your player selection on the Web system.",
    )
    parser.add_argument(
        "--opponent-source",
        choices=("own", "direct", "default"),
        default="direct",
        help="Source for opponent player selection on the Web system.",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL of the Web system.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for saved JSON responses.",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Poll created matches and save the latest match JSON.",
    )
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--poll-attempts", type=int, default=60)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print request bodies without sending API requests.",
    )
    return parser.parse_args()


def api_request(
    method: str,
    base_url: str,
    path: str,
    token: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    token = normalize_auth_token(token)
    request = Request(
        base_url.rstrip("/") + path,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {exc.reason}: {error_body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Request failed: {exc.reason}") from exc

    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Response was not JSON: {raw[:500]}") from exc


def normalize_auth_token(token: str) -> str:
    token = token.strip()
    if token.lower().startswith("bearer "):
        return token[7:].strip()
    return token


def selection(player_id: str, source: str) -> dict[str, str]:
    return {"playerId": player_id.strip(), "source": source}


def match_payload(args: argparse.Namespace, index: int) -> dict[str, Any]:
    my_is_black_first = args.start_color == "black"
    my_is_black = my_is_black_first if index % 2 == 0 else not my_is_black_first
    mine = selection(args.my_player_id, args.my_source)
    opponent = selection(args.opponent_id, args.opponent_source)
    return {
        "blackPlayer": mine if my_is_black else opponent,
        "whitePlayer": opponent if my_is_black else mine,
    }


def extract_match_id(response: Any) -> str | None:
    if isinstance(response, dict):
        for key in ("id", "matchId"):
            value = response.get(key)
            if isinstance(value, str) and value:
                return value
        for value in response.values():
            found = extract_match_id(value)
            if found:
                return found
    elif isinstance(response, list):
        for value in response:
            found = extract_match_id(value)
            if found:
                return found
    return None


def default_output_dir() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path("generated_kihu") / "for_training" / "vs_TA_Player_v2_web" / stamp


def append_jsonl(path: Path, value: Any) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(value, ensure_ascii=False, sort_keys=True))
        f.write("\n")


def main() -> int:
    args = parse_args()
    if args.games <= 0:
        print("ERROR: --games must be positive.", file=sys.stderr)
        return 2

    out_dir = Path(args.output_dir) if args.output_dir else default_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    requests_path = out_dir / "requests.jsonl"
    created_path = out_dir / "created_matches.jsonl"
    polled_path = out_dir / "polled_matches.jsonl"

    token = normalize_auth_token(os.environ.get("OTHELLOPY_AUTH_TOKEN", ""))
    if not token and not args.dry_run:
        print("ERROR: Set OTHELLOPY_AUTH_TOKEN or use --dry-run.", file=sys.stderr)
        return 2

    created_ids: list[str] = []
    for i in range(args.games):
        payload = match_payload(args, i)
        request_record = {"index": i + 1, "payload": payload}
        append_jsonl(requests_path, request_record)

        if args.dry_run:
            print(json.dumps(request_record, ensure_ascii=False))
            continue

        response = api_request("POST", args.base_url, "/api/matches", token, payload)
        match_id = extract_match_id(response)
        append_jsonl(created_path, {"index": i + 1, "matchId": match_id, "response": response})
        print(f"created {i + 1}/{args.games}: matchId={match_id or 'unknown'}")
        if match_id:
            created_ids.append(match_id)

    if args.wait and not args.dry_run:
        for match_id in created_ids:
            path = f"/api/matches/{quote(match_id, safe='')}"
            latest: dict[str, Any] | None = None
            for attempt in range(1, args.poll_attempts + 1):
                latest = api_request("GET", args.base_url, path, token)
                append_jsonl(
                    polled_path,
                    {"matchId": match_id, "attempt": attempt, "response": latest},
                )
                status = str(latest.get("status", latest.get("state", ""))).lower()
                print(f"poll {match_id}: attempt={attempt} status={status or 'unknown'}")
                if status in {"completed", "complete", "finished", "done", "failed", "error"}:
                    break
                time.sleep(args.poll_interval)

    summary = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "games": args.games,
        "myPlayerId": args.my_player_id,
        "opponentId": args.opponent_id,
        "outputDir": str(out_dir),
        "createdMatchIds": created_ids,
        "dryRun": args.dry_run,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"saved: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
