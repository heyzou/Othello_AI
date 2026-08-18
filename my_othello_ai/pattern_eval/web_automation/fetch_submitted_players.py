#!/usr/bin/env python3
"""Fetch submitted player codes from othellopy.com and save to players/submitted/."""

import os
import re
import json
import ast
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

DEST_DIR = "my_othello_ai/pattern_eval/players/submitted"
TOKEN_FILE = "my_othello_ai/pattern_eval/secrets/othellopy_token.env"

WHITELIST = {'bisect', 'collections', 'copy', 'dataclasses', 'enum', 'functools', 'heapq', 'itertools', 'math', 'operator', 'othellopy', 'random', 'statistics', 'typing'}
FORBIDDEN_NAMES = {'breakpoint', 'compile', 'delattr', 'input', 'locals', 'open', 'setattr', 'vars'}
FORBIDDEN_ATTRS = {'__class__', '__dict__', '__globals__', '__mro__', '__subclasses__'}

TARGET_VERSIONS = [
    "v47", "v48",
    "v77", "v78", "v79", "v80",
    "v81", "v82", "v83", "v84", "v85", "v86", "v87", "v88", "v89", "v90",
    "v98", "v100", "v101", "v102"
]

def get_token():
    token = os.environ.get("OTHELLOPY_AUTH_TOKEN", "")
    if not token and os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("OTHELLOPY_AUTH_TOKEN="):
                    token = line.strip().split("=", 1)[1].strip("\"' ")
                elif line.strip().startswith("eyJ"):
                    token = line.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    return token

def api_get(url, token):
    req = Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    })
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def clean_and_validate(code_str, filename):
    # Strip any dangerous/forbidden imports if present
    code = re.sub(r'^\s*import time\s*\n', '', code_str, flags=re.MULTILINE)
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return code, [f"SyntaxError: {e}"]
    
    errors = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                root = name.name.split('.')[0]
                if root not in WHITELIST:
                    errors.append(f"Forbidden import: {root}")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split('.')[0]
                if root not in WHITELIST:
                    errors.append(f"Forbidden import: {node.module}")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES and isinstance(node.ctx, ast.Load):
            errors.append(f"Forbidden name load: {node.id}")
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRS:
            errors.append(f"Forbidden attr: {node.attr}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {'eval', 'exec', 'open'}:
            errors.append(f"Forbidden call: {node.func.id}()")
    return code, errors

def main():
    token = get_token()
    if not token:
        print("ERROR: OTHELLOPY_AUTH_TOKEN is missing or empty.")
        return 1
    
    os.makedirs(DEST_DIR, exist_ok=True)
    print("Fetching player list from https://othellopy.com/api/players...")
    
    all_own_players = []
    cursor = None
    while True:
        params = {}
        if cursor:
            params['cursor'] = cursor
        url = 'https://othellopy.com/api/players'
        if params:
            url += '?' + urlencode(params)
        
        data = api_get(url, token)
        own = data.get('ownPlayers', [])
        all_own_players.extend(own)
        cursor = data.get('ownPlayersNextCursor')
        if not cursor or not own:
            break
    
    print(f"Total own players found on othellopy.com: {len(all_own_players)}")
    
    # Group by player name to handle duplicates like v90
    players_by_name = {}
    for p in all_own_players:
        name = p.get("playerName", "").strip()
        if name not in players_by_name:
            players_by_name[name] = []
        players_by_name[name].append(p)

    saved_count = 0
    for target in TARGET_VERSIONS:
        matched = players_by_name.get(target, [])
        if not matched:
            print(f"  [MISSING] {target} not found on server")
            continue
        
        # If multiple (e.g. v90), sort by createdAt ascending
        matched.sort(key=lambda x: x.get("createdAt", ""))
        
        for idx, p in enumerate(matched):
            p_id = p.get("playerId")
            created_at = p.get("createdAt")
            
            # Name suffix if multiple
            if len(matched) > 1:
                filename = f"{target}_{idx+1}.py"
            else:
                filename = f"{target}.py"
            
            print(f"Fetching code for {filename} (ID: {p_id}, Created: {created_at})...")
            detail = api_get(f"https://othellopy.com/api/players/{p_id}", token)
            code = detail.get("sourceCode") or detail.get("code")
            
            if not code:
                print(f"    WARNING: No code returned for {p_id}")
                continue
                
            clean_code, errs = clean_and_validate(code, filename)
            file_path = os.path.join(DEST_DIR, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(clean_code)
            
            status = "VALID" if not errs else f"WARNINGS: {errs}"
            print(f"    Saved -> {file_path} ({status})")
            saved_count += 1
            
    print(f"\nCompleted! Successfully synced {saved_count} player files into {DEST_DIR}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
