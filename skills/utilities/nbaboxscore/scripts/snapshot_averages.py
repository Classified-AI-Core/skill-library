#!/usr/bin/env python3.12
"""Snapshot all NBA player season averages to a JSON file.

Usage:
    python3.12 snapshot_averages.py

Outputs: ../data/season_averages.json
"""

import json
import os
import sys
import time
from datetime import UTC, datetime

from nba_api.stats.endpoints import leaguedashplayerstats

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "season_averages.json")

MAX_RETRIES = int(os.getenv("NBA_SNAPSHOT_MAX_RETRIES", "1"))
TIMEOUT = int(os.getenv("NBA_SNAPSHOT_TIMEOUT", "20"))


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print("Fetching league-wide player stats (per game)...", file=sys.stderr)

    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            stats = leaguedashplayerstats.LeagueDashPlayerStats(
                per_mode_detailed="PerGame",
                season="2025-26",
                season_type_all_star="Regular Season",
                timeout=TIMEOUT,
            )
            last_err = None
            break
        except Exception as e:
            last_err = e
            if attempt < MAX_RETRIES:
                wait = min(10, attempt * 5)
                print(f"  Attempt {attempt} failed ({type(e).__name__}), retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
            continue

    if last_err:
        # API unreachable — keep existing data, mark as stale
        existing_path = OUTPUT_FILE + ".stale"
        if os.path.exists(OUTPUT_FILE):
            import shutil

            shutil.copy(OUTPUT_FILE, existing_path)
        with open(existing_path, "w") as f:
            json.dump({"error": str(last_err), "failed_at": utc_stamp()}, f)
        print(f"API unreachable ({type(last_err).__name__}), existing data preserved.", file=sys.stderr)
        sys.exit(0)

    data = stats.get_dict()

    result_set = None
    for rs in data["resultSets"]:
        if rs["name"] == "LeagueDashPlayerStats":
            result_set = rs
            break

    if not result_set:
        print("ERROR: Could not find LeagueDashPlayerStats result set", file=sys.stderr)
        sys.exit(1)

    headers = result_set["headers"]
    rows = result_set["rowSet"]

    player_avgs = {}
    for row in rows:
        d = dict(zip(headers, row))
        pid = d["PLAYER_ID"]
        player_avgs[str(pid)] = {
            "PLAYER_NAME": d.get("PLAYER_NAME", ""),
            "TEAM": d.get("TEAM_ABBREVIATION", ""),
            "GP": d.get("GP", 0),
            "MIN": d.get("MIN", 0),
            "PTS": d.get("PTS", 0),
            "REB": d.get("REB", 0),
            "AST": d.get("AST", 0),
            "STL": d.get("STL", 0),
            "BLK": d.get("BLK", 0),
            "FG3M": d.get("FG3M", 0),
            "TOV": d.get("TOV", 0),
            "FGM": d.get("FGM", 0),
            "FGA": d.get("FGA", 0),
        }

    output = {
        "snapshot_date": utc_stamp(),
        "season": "2025-26",
        "player_count": len(player_avgs),
        "players": player_avgs,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Saved {len(player_avgs)} player averages to {OUTPUT_FILE}", file=sys.stderr)
    print(f"Snapshot: {output['snapshot_date']} — {len(player_avgs)} players")


if __name__ == "__main__":
    main()
