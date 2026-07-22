---
name: nbaboxscore
description: >
  Retrieve NBA box score stats and generate a report with notable performances for a specific team's game. Use when the
  user asks for a box score report, game recap, or notable stats from an NBA game played today or last night. Triggers:
  "box score", "boxscore", "how did the [team] do", "game report", "[team] game last night", "what happened in the
  [team] game".
compatibility: Created for Zo Computer
metadata:
  author: zmann.zo.computer
  category: productivity
  maturity: stable
  tags:
    - nbaboxscore
    - automation
    - analysis
    - export
    - python
  related:
    - fal-generate
    - fal-audio
    - fal-video-edit
    - fal-vision
---

## Usage

When the user asks about an NBA game box score, run:

```bash
python3.12 /home/workspace/Skills/nbaboxscore/scripts/boxscore.py --team "<TEAM>" [--date YYYY-MM-DD]
```

**Arguments:**
- `--team` (required): Team name, city, or tricode. Examples: `"Knicks"`, `"NYK"`, `"New York"`
- `--date` (optional): Game date in `YYYY-MM-DD`. If omitted, auto-checks today first, then yesterday.

**Output includes:**
1. **Game Summary** — Final score, quarter-by-quarter breakdown, narrative (blowout/close game/comeback/OT)
2. **Notable Performances** — Players with abnormal stat lines compared to season averages
3. **Full Box Score** — All players with MIN, PTS, REB, AST, STL, BLK, FG, 3PT, FT, TOV, +/-
4. **Game Leaders** — Top performers per team

**Notable detection thresholds:**
- Absolute: 30+ PTS, 10+ REB, 10+ AST, 4+ STL, 4+ BLK, 6+ 3PM, 7+ TOV
- Relative: 2x+ season average in PTS/REB/AST, 3x+ in STL/BLK, 2.5x+ in 3PM
- Efficiency: 65%+ FG on 10+ attempts, or sub-25% FG on 12+ attempts
- Milestones: triple-doubles, double-doubles
- Minutes: 1.5x+ or 0.5x average minutes

## Season Averages Snapshot

Player season averages are pre-cached in `data/season_averages.json` (~569 players).
A scheduled agent refreshes this snapshot daily at 6:00 AM ET.

To manually refresh:
```bash
python3.12 /home/workspace/Skills/nbaboxscore/scripts/snapshot_averages.py
```

