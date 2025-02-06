# NFL Big Data Bowl 2025

This document provides an overview of the raw data provided for the NFL Big Data Bowl 2025 competition on Kaggle.

## Dataset Overview

The dataset for the NFL Big Data Bowl 2025 contains detailed tracking data, player information, and game details from NFL games. The data is designed to help participants analyze player performance, team strategies, and other aspects of the game.

## Data Source

The data is provided by the National Football League (NFL) and is available on the [Kaggle competition page](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data).

## File descriptions

- `Game data:` The games.csv contains the teams playing in each game. The key variable is gameId.

- `Play data:` The plays.csv file contains play-level information from each game. The key variables are gameId and playId.

- `Player data:` The players.csv file contains player-level information from players that participated in any of the tracking data files. The key variable is nflId.

- `Player play data:` The player_play.csv file contains player-level stats for each game and play. The key variables are gameId, playId, and nflId.

- `Tracking data:` Files tracking_week_[week].csv contain player tracking data from week number [week]. The key variables are gameId, playId, and nflId.


## Data Dictionary

A detailed data dictionary is available on the Kaggle competition page, providing descriptions of each column in the dataset.

## Usage

This data is intended for use in the NFL Big Data Bowl 2025 competition. Participants are encouraged to explore the data, perform analyses, and develop models to gain insights into NFL gameplay and player performance.

## License

The data is provided under the [NFL Big Data Bowl 2025 Competition License](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/rules).

## Acknowledgments

- **National Football League (NFL)** for providing the data.
- **Kaggle** for hosting the competition.

---

For more details, visit the [competition page](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025) on Kaggle.