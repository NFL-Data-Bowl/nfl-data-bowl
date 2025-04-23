# Merging all the data
This script processes raw tracking and player-level data to generate a flattened, play-level dataset for machine learning modeling.

Sample_Data/Raw/: Contains raw tracking data (tracking_week_*.csv)
Sample_Data/data_dir_processed/: Contains preprocessed .parquet files (e.g., plays.parquet, player_play.parquet)

> **_NOTE:_**  I removed all the featues that can influence the result manualy before.


## What the Script Does

#### Tracking Data Preprocessing (frame_to_nflid):

1. Filters for frameType == "BEFORE_SNAP" to only keep data before the ball is snapped.

2. Aggregates player movement stats (speed, acceleration, distance, x/y position, direction) by gameId, playId, and nflId.

#### Merge Tracking with Player-Play Data:

1. Loads player_play.parquet (includes player roles and coverage assignments)

2. Merges it with the tracking summary to get one row per player per play.

#### Flatten to Play-Level (player_level_to_play_level):

1. Transforms the dataset from one row per player to one row per play, by:

2. Grouping players by pff_defensiveCoverageAssignment

3. Flattening each player’s stats into their own set of columns (e.g., MAN_1_s_mean, ZONE_2_dis_sum)

4. Assigning a fixed number of player columns per role (fills missing with zeros)

#### Merge with Play Data: 

1. Joins the final play-level dataframe with the full plays.parquet metadata for downstream use.

#### Save Output:

Outputs a single .parquet file for modeling.


