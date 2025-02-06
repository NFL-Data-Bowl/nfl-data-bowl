## List of Raw Datasets


| Raw Dataset Name | Link to the Full Dataset | Full Dataset Size (MB) |
|-----------------|--------------------------|------------------------|
| `games.csv` | [link](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data?select=games.csv) | 0.007 |
| `player_play.csv` | [link](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data?select=player_play.csv) | 51.00 |
| `players.csv` | [link](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data?select=players.csv) | 0.103 |
| `plays.csv` | [link](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data?select=plays.csv) | 6.60 |
| `tracking_week_1.csv` | [link](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data?select=tracking_week_1.csv) | 927.00 |
| `tracking_week_2.csv` | [link](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data?select=tracking_week_2.csv) | 874.00 |
| `tracking_week_3.csv` | [link](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data?select=tracking_week_3.csv) | 931.00 |
| `tracking_week_4.csv` | [link](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data?select=tracking_week_4.csv) | 880.00 |
| `tracking_week_5.csv` | [link](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data?select=tracking_week_5.csv) | 927.00 |
| `tracking_week_6.csv` | [link](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data?select=tracking_week_6.csv) | 813.00 |
| `tracking_week_7.csv` | [link](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data?select=tracking_week_7.csv) | 787.00 |
| `tracking_week_8.csv` | [link](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data?select=tracking_week_8.csv) | 862.00 |
| `tracking_week_9.csv` | [link](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data?select=tracking_week_9.csv) | 739.00 |


## Notes:
1. Accessing the Full Dataset: 
    
    The full dataset is available on the NFL Big Data Bowl 2025 Kaggle competition page. You will need to:

    - Sign up for a Kaggle account.
    - Accept the competition rules.
    - Join the competition to download the data.

---
## Dataset Descriptions

### Game Data (`games.csv`)
- **Description**: Contains game-level information, including teams, scores, and game dates.
- **Key Variables**:
  - `gameId`: Unique game identifier.
  - `season`: Season of the game.
  - `week`: Week of the game.
  - `gameDate`: Date of the game.
  - `homeTeamAbbr`: Home team abbreviation.
  - `visitorTeamAbbr`: Visiting team abbreviation.
  - `homeFinalScore`: Total points scored by the home team.
  - `visitorFinalScore`: Total points scored by the visiting team.

---

### Play Data (`plays.csv`)
- **Description**: Contains play-level information, including play descriptions, down, distance, and outcomes.
- **Key Variables**:
  - `gameId`: Unique game identifier.
  - `playId`: Unique play identifier (within a game).
  - `playDescription`: Description of the play.
  - `quarter`: Quarter of the game.
  - `down`: Down number.
  - `yardsToGo`: Distance needed for a first down.
  - `possessionTeam`: Team on offense.
  - `defensiveTeam`: Team on defense.
  - `yardlineNumber`: Yard line at the line of scrimmage.
  - `absoluteYardlineNumber`: Distance from the end zone for the possession team.

---

### Player Data (`players.csv`)
- **Description**: Contains player-level information, including height, weight, position, and college.
- **Key Variables**:
  - `nflId`: Unique player identifier.
  - `height`: Player height.
  - `weight`: Player weight.
  - `position`: Player position.
  - `displayName`: Player name.

---

### Player Play Data (`player_play.csv`)
- **Description**: Contains player-level stats for each game and play, including rushing, passing, and receiving stats.
- **Key Variables**:
  - `gameId`: Unique game identifier.
  - `playId`: Unique play identifier.
  - `nflId`: Unique player identifier.
  - `teamAbbr`: Team abbreviation.
  - `rushingYards`: Yards gained by the player on rushing attempts.
  - `passingYards`: Yards gained by the player on passing attempts.
  - `receivingYards`: Yards gained by the player on receptions.
  - `fumbles`: Number of fumbles by the player.

---

### Tracking Data (`tracking_week_[week].csv`)
- **Description**: Contains player tracking data for each play, including position, speed, and direction.
- **Key Variables**:
  - `gameId`: Unique game identifier.
  - `playId`: Unique play identifier.
  - `nflId`: Unique player identifier (or NA for the ball).
  - `x`: Player position along the long axis of the field.
  - `y`: Player position along the short axis of the field.
  - `s`: Speed in yards/second.
  - `a`: Acceleration in yards/second².
  - `dir`: Angle of player motion.

---

## Supplemental Data
The **2025 Big Data Bowl** allows participants to use supplemental NFL data (e.g., from **nflverse** or **Pro Football Reference**) as long as it is free and publicly available.

- The `gameId` and `playId` in the **Big Data Bowl** data can be merged with `old_game_id` and `play_id` in **nflverse's** play-by-play data.


This document provides a comprehensive overview of the **raw datasets** for the **NFL Big Data Bowl 2025** competition, including dataset descriptions, key variables, and instructions for accessing the data.
