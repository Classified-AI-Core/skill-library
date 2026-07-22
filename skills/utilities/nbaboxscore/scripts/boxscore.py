#!/usr/bin/env python3.12
"""NBA Box Score Report Generator.

Fetches box score data for a specific team's game (today or yesterday),
compares player stats against season averages, and generates a markdown
report with notable performances and game narrative.

Usage:
    python3.12 boxscore.py --team TEAM [--date DATE]
    python3.12 boxscore.py --team "Knicks"
    python3.12 boxscore.py --team "NYK" --date 2026-03-22

Options:
    --team   Team name, city, or tricode (e.g. "Knicks", "New York", "NYK")
    --date   Game date in YYYY-MM-DD format. Defaults to smart resolution:
             checks today first, then yesterday.
    --help   Show this help message.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

from nba_api.stats.endpoints import (
    boxscoretraditionalv3,
    scoreboardv3,
)
from nba_api.stats.static import teams as nba_teams

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AVERAGES_FILE = os.path.join(SCRIPT_DIR, "..", "data", "season_averages.json")
_averages_cache: dict | None = None


def load_averages() -> dict:
    global _averages_cache
    if _averages_cache is not None:
        return _averages_cache
    if not os.path.exists(AVERAGES_FILE):
        print("WARNING: No season_averages.json found. Run snapshot_averages.py first.", file=sys.stderr)
        _averages_cache = {}
        return _averages_cache
    with open(AVERAGES_FILE) as f:
        data = json.load(f)
    _averages_cache = data.get("players", {})
    snap_date = data.get("snapshot_date", "unknown")
    print(f"Loaded season averages snapshot from {snap_date}", file=sys.stderr)
    return _averages_cache


def find_team(query: str) -> dict | None:
    query_lower = query.strip().lower()
    all_teams = nba_teams.get_teams()
    for t in all_teams:
        if query_lower in (
            t["abbreviation"].lower(),
            t["nickname"].lower(),
            t["city"].lower(),
            t["full_name"].lower(),
        ):
            return t
    for t in all_teams:
        if query_lower in t["full_name"].lower() or query_lower in t["nickname"].lower():
            return t
    return None


def get_games_for_date(date_str: str) -> list[dict]:
    sb = scoreboardv3.ScoreboardV3(game_date=date_str)
    data = sb.get_dict()
    return data.get("scoreboard", {}).get("games", [])


def find_team_game(team_id: int, games: list[dict]) -> dict | None:
    for g in games:
        if g["homeTeam"]["teamId"] == team_id or g["awayTeam"]["teamId"] == team_id:
            return g
    return None


def get_box_score(game_id: str) -> dict:
    box = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game_id)
    return box.get_dict()["boxScoreTraditional"]


def get_season_averages(player_id: int) -> dict | None:
    avgs = load_averages()
    return avgs.get(str(player_id))


def parse_minutes(min_str: str) -> float:
    if not min_str or min_str == "":
        return 0.0
    parts = min_str.split(":")
    if len(parts) == 2:
        return int(parts[0]) + int(parts[1]) / 60
    return float(parts[0])


def detect_notable(player_name: str, game_stats: dict, season_avg: dict | None) -> list[str]:
    notes = []
    pts = game_stats.get("points", 0)
    reb = game_stats.get("reboundsTotal", 0)
    ast = game_stats.get("assists", 0)
    stl = game_stats.get("steals", 0)
    blk = game_stats.get("blocks", 0)
    fg3m = game_stats.get("threePointersMade", 0)
    tov = game_stats.get("turnovers", 0)
    mins = parse_minutes(game_stats.get("minutes", "0:00"))

    # Absolute thresholds
    if pts >= 40:
        notes.append(f"**{pts} PTS** — 40-point explosion")
    elif pts >= 30:
        notes.append(f"**{pts} PTS** — 30-piece")

    if reb >= 15:
        notes.append(f"**{reb} REB** — dominant on the glass")
    elif reb >= 10:
        notes.append(f"**{reb} REB** — double-digit boards")

    if ast >= 12:
        notes.append(f"**{ast} AST** — elite playmaking")
    elif ast >= 10:
        notes.append(f"**{ast} AST** — double-digit dimes")

    if stl >= 4:
        notes.append(f"**{stl} STL** — pickpocket performance")

    if blk >= 4:
        notes.append(f"**{blk} BLK** — rim protection showcase")

    if fg3m >= 7:
        notes.append(f"**{fg3m} 3PM** — scorching from deep")
    elif fg3m >= 6:
        notes.append(f"**{fg3m} 3PM** — lights out from three")

    if tov >= 7:
        notes.append(f"**{tov} TOV** — turnover-prone outing")

    # Triple-double / double-double
    doubles = sum(1 for x in [pts, reb, ast, stl, blk] if x >= 10)
    if doubles >= 3:
        notes.append("**TRIPLE-DOUBLE**")
    elif doubles >= 2:
        cats = []
        if pts >= 10: cats.append(f"{pts}p")
        if reb >= 10: cats.append(f"{reb}r")
        if ast >= 10: cats.append(f"{ast}a")
        if stl >= 10: cats.append(f"{stl}s")
        if blk >= 10: cats.append(f"{blk}b")
        notes.append(f"**Double-double** ({'/'.join(cats)})")

    # Compare to season averages
    if season_avg:
        avg_pts = season_avg.get("PTS", 0) or 0
        avg_reb = season_avg.get("REB", 0) or 0
        avg_ast = season_avg.get("AST", 0) or 0
        avg_stl = season_avg.get("STL", 0) or 0
        avg_blk = season_avg.get("BLK", 0) or 0
        avg_fg3m = season_avg.get("FG3M", 0) or 0
        avg_min = season_avg.get("MIN", 0) or 0

        if avg_pts > 5 and pts >= avg_pts * 2:
            notes.append(f"Scored **{pts}** on a **{avg_pts:.1f}** season avg — **{pts/avg_pts:.1f}x** his average")
        elif avg_pts > 5 and pts <= avg_pts * 0.3 and mins > 15:
            notes.append(f"Only **{pts} PTS** on **{avg_pts:.1f}** avg — rough night scoring")

        if avg_reb > 3 and reb >= avg_reb * 2:
            notes.append(f"**{reb} REB** vs **{avg_reb:.1f}** avg — **{reb/avg_reb:.1f}x** his average")

        if avg_ast > 2 and ast >= avg_ast * 2:
            notes.append(f"**{ast} AST** vs **{avg_ast:.1f}** avg — **{ast/avg_ast:.1f}x** his average")

        if avg_stl > 0.5 and stl >= avg_stl * 3:
            notes.append(f"**{stl} STL** vs **{avg_stl:.1f}** avg — active hands")

        if avg_blk > 0.5 and blk >= avg_blk * 3:
            notes.append(f"**{blk} BLK** vs **{avg_blk:.1f}** avg — swatting everything")

        if avg_fg3m > 1 and fg3m >= avg_fg3m * 2.5:
            notes.append(f"**{fg3m} 3PM** vs **{avg_fg3m:.1f}** avg — hot from deep")

        if avg_min > 10 and mins >= avg_min * 1.5:
            notes.append(f"Played **{mins:.0f} min** vs **{avg_min:.1f}** avg — heavy workload")
        elif avg_min > 15 and mins <= avg_min * 0.5 and mins > 0:
            notes.append(f"Only **{mins:.0f} min** vs **{avg_min:.1f}** avg — limited minutes")

    # Efficiency: high points on low attempts
    fga = game_stats.get("fieldGoalsAttempted", 0)
    fgm = game_stats.get("fieldGoalsMade", 0)
    if fga >= 10 and fgm / fga >= 0.65:
        notes.append(f"Ultra-efficient: **{fgm}/{fga} FG** ({fgm/fga:.1%})")
    elif fga >= 12 and fgm / fga <= 0.25:
        notes.append(f"Rough shooting: **{fgm}/{fga} FG** ({fgm/fga:.1%})")

    return notes


def game_narrative(scoreboard_game: dict, box_data: dict) -> str:
    home = scoreboard_game["homeTeam"]
    away = scoreboard_game["awayTeam"]
    home_score = home["score"]
    away_score = away["score"]
    home_tri = home["teamTricode"]
    away_tri = away["teamTricode"]
    margin = abs(home_score - away_score)
    winner_tri = home_tri if home_score > away_score else away_tri
    loser_tri = away_tri if home_score > away_score else home_tri
    winner_score = max(home_score, away_score)
    loser_score = min(home_score, away_score)

    # Check for OT
    periods = home.get("periods", [])
    ot_count = sum(1 for p in periods if p.get("period", 0) > 4 and p.get("score", 0) > 0)

    # Quarter-by-quarter
    lines = []
    lines.append(f"## Game Summary")
    lines.append(f"**{away_tri} {away_score}** {'@' if True else 'vs'} **{home_tri} {home_score}** — **{winner_tri} wins**")
    lines.append("")

    # Quarter scores
    home_periods = home.get("periods", [])
    away_periods = away.get("periods", [])
    if home_periods:
        header = "| | " + " | ".join(
            f"Q{p['period']}" if p['period'] <= 4 else f"OT{p['period']-4}"
            for p in home_periods if p.get("score", 0) > 0 or p["period"] <= 4
        ) + " | **Total** |"
        sep = "|" + "---|" * (len([p for p in home_periods if p.get("score", 0) > 0 or p["period"] <= 4]) + 2)
        away_row = f"| **{away_tri}** | " + " | ".join(
            str(p["score"]) for p in away_periods if p.get("score", 0) > 0 or p["period"] <= 4
        ) + f" | **{away_score}** |"
        home_row = f"| **{home_tri}** | " + " | ".join(
            str(p["score"]) for p in home_periods if p.get("score", 0) > 0 or p["period"] <= 4
        ) + f" | **{home_score}** |"
        lines.extend([header, sep, away_row, home_row, ""])

    # Narrative
    if ot_count > 0:
        lines.append(f"A **{'double ' if ot_count == 2 else 'triple ' if ot_count == 3 else ''}{ot_count}OT thriller** — {winner_tri} outlasts {loser_tri} **{winner_score}-{loser_score}**.")
    elif margin <= 3:
        lines.append(f"**Nail-biter.** {winner_tri} edges {loser_tri} by just **{margin}** in a game that came down to the wire.")
    elif margin <= 6:
        lines.append(f"**Close game.** {winner_tri} holds off {loser_tri} by **{margin}** — competitive throughout.")
    elif margin <= 12:
        lines.append(f"**Comfortable win** for {winner_tri} by **{margin}** — they controlled the pace.")
    elif margin <= 20:
        lines.append(f"**Dominant performance** by {winner_tri} — a **{margin}-point** beatdown of {loser_tri}.")
    else:
        lines.append(f"**Blowout.** {winner_tri} buries {loser_tri} by **{margin}** — this one was over early.")

    # 4th quarter narrative
    if len(home_periods) >= 4 and len(away_periods) >= 4:
        h_q4 = home_periods[3].get("score", 0)
        a_q4 = away_periods[3].get("score", 0)
        h_q3_total = sum(p.get("score", 0) for p in home_periods[:3])
        a_q3_total = sum(p.get("score", 0) for p in away_periods[:3])
        lead_entering_4th = h_q3_total - a_q3_total  # positive = home led

        if lead_entering_4th > 0 and home_score < away_score:
            lines.append(f"{home_tri} led by **{lead_entering_4th}** entering the 4th but {away_tri} stormed back — **{a_q4}-{h_q4}** in Q4.")
        elif lead_entering_4th < 0 and away_score < home_score:
            lines.append(f"{away_tri} led by **{abs(lead_entering_4th)}** entering the 4th but {home_tri} mounted a comeback — **{h_q4}-{a_q4}** in Q4.")

        # Check if a team had a monster quarter
        for i, (hp, ap) in enumerate(zip(home_periods[:4], away_periods[:4])):
            qnum = i + 1
            if hp.get("score", 0) >= 40:
                lines.append(f"{home_tri} erupted for **{hp['score']} points** in Q{qnum}.")
            if ap.get("score", 0) >= 40:
                lines.append(f"{away_tri} erupted for **{ap['score']} points** in Q{qnum}.")

    lines.append("")
    return "\n".join(lines)


def format_box_score_table(team_data: dict, team_tri: str) -> str:
    lines = []
    lines.append(f"### {team_data['teamCity']} {team_data['teamName']} ({team_tri})")
    lines.append("")
    lines.append("| Player | MIN | PTS | REB | AST | STL | BLK | FG | 3PT | FT | TOV | +/- |")
    lines.append("|--------|-----|-----|-----|-----|-----|-----|----|----|----|----|-----|")

    players = sorted(
        team_data["players"],
        key=lambda p: parse_minutes(p["statistics"].get("minutes", "0:00")),
        reverse=True,
    )

    for p in players:
        s = p["statistics"]
        mins = s.get("minutes", "0:00")
        if parse_minutes(mins) == 0:
            continue
        name = f"{p['firstName'][0]}. {p['familyName']}"
        fg = f"{s['fieldGoalsMade']}-{s['fieldGoalsAttempted']}"
        tp = f"{s['threePointersMade']}-{s['threePointersAttempted']}"
        ft = f"{s['freeThrowsMade']}-{s['freeThrowsAttempted']}"
        pm = s.get("plusMinusPoints", 0)
        pm_str = f"+{pm:.0f}" if pm > 0 else f"{pm:.0f}"
        lines.append(
            f"| {name} | {mins} | {s['points']} | {s['reboundsTotal']} | "
            f"{s['assists']} | {s['steals']} | {s['blocks']} | {fg} | {tp} | {ft} | "
            f"{s['turnovers']} | {pm_str} |"
        )

    # Team totals
    ts = team_data["statistics"]
    lines.append(
        f"| **TOTAL** | {ts['minutes']} | **{ts['points']}** | **{ts['reboundsTotal']}** | "
        f"**{ts['assists']}** | **{ts['steals']}** | **{ts['blocks']}** | "
        f"{ts['fieldGoalsMade']}-{ts['fieldGoalsAttempted']} ({ts['fieldGoalsPercentage']:.1%}) | "
        f"{ts['threePointersMade']}-{ts['threePointersAttempted']} ({ts['threePointersPercentage']:.1%}) | "
        f"{ts['freeThrowsMade']}-{ts['freeThrowsAttempted']} ({ts['freeThrowsPercentage']:.1%}) | "
        f"**{ts['turnovers']}** | |"
    )
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="NBA Box Score Report")
    parser.add_argument("--team", required=True, help="Team name, city, or tricode")
    parser.add_argument("--date", default=None, help="Game date (YYYY-MM-DD). Auto-resolves today/yesterday if omitted.")
    args = parser.parse_args()

    team = find_team(args.team)
    if not team:
        print(f"Could not find team matching '{args.team}'.")
        print("Try a tricode (NYK), nickname (Knicks), or city (New York).")
        sys.exit(1)

    team_id = team["id"]
    team_name = team["full_name"]
    team_tri = team["abbreviation"]
    print(f"Looking up game for **{team_name}** ({team_tri})...\n", file=sys.stderr)

    # Find the game
    game = None
    game_date = None

    if args.date:
        games = get_games_for_date(args.date)
        game = find_team_game(team_id, games)
        game_date = args.date
    else:
        # Smart resolution: check today first, then yesterday
        today = datetime.utcnow().strftime("%Y-%m-%d")
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

        games = get_games_for_date(today)
        game = find_team_game(team_id, games)
        if game and game.get("gameStatus", 1) == 3:
            game_date = today
        else:
            game = None
            games = get_games_for_date(yesterday)
            game = find_team_game(team_id, games)
            game_date = yesterday

    if not game:
        print(f"No completed game found for {team_name}.")
        if not args.date:
            print("Checked today and yesterday. Try specifying --date.")
        sys.exit(1)

    game_id = game["gameId"]
    game_status = game.get("gameStatusText", "")
    if game.get("gameStatus", 1) != 3:
        print(f"Game found but status is: {game_status}")
        print("Box score is only available for completed games.")
        sys.exit(1)

    # Fetch box score
    print(f"Fetching box score for game {game_id} on {game_date}...\n", file=sys.stderr)
    box = get_box_score(game_id)

    home_team = box["homeTeam"]
    away_team = box["awayTeam"]

    # Build report
    report = []
    report.append(f"# NBA Box Score Report — {game_date}")
    report.append("")

    # Game narrative
    report.append(game_narrative(game, box))

    # Notable performances
    report.append("## Notable Performances")
    report.append("")

    all_players = []
    for team_data in [away_team, home_team]:
        tri = team_data["teamTricode"]
        for p in team_data["players"]:
            s = p["statistics"]
            if parse_minutes(s.get("minutes", "0:00")) < 5:
                continue
            name = f"{p['firstName']} {p['familyName']}"
            all_players.append((p["personId"], name, tri, s))

    notable_entries = []
    for pid, name, tri, stats in all_players:
        avg = get_season_averages(pid)
        notes = detect_notable(name, stats, avg)
        if notes:
            notable_entries.append((name, tri, stats, notes))

    if notable_entries:
        for name, tri, stats, notes in notable_entries:
            pts = stats.get("points", 0)
            reb = stats.get("reboundsTotal", 0)
            ast = stats.get("assists", 0)
            report.append(f"**{name}** ({tri}) — {pts} PTS / {reb} REB / {ast} AST")
            for n in notes:
                report.append(f"  - {n}")
            report.append("")
    else:
        report.append("No standout anomalies detected — a balanced, normal-stat game.\n")

    # Full box scores
    report.append("---")
    report.append("")
    report.append(format_box_score_table(away_team, away_team["teamTricode"]))
    report.append(format_box_score_table(home_team, home_team["teamTricode"]))

    # Game leaders
    leaders = game.get("gameLeaders", {})
    if leaders:
        report.append("## Game Leaders")
        report.append("")
        for side in ["homeLeaders", "awayLeaders"]:
            l = leaders.get(side, {})
            if l and l.get("name"):
                report.append(f"- **{l['name']}** ({l.get('teamTricode', '?')}): {l.get('points', 0)} PTS / {l.get('rebounds', 0)} REB / {l.get('assists', 0)} AST")
        report.append("")

    print("\n".join(report))


if __name__ == "__main__":
    main()
