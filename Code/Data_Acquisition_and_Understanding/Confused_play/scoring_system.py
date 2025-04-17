
import pandas as pd
import numpy as np

def receiver_is_wide_open(play_row, tracking_df):
    game_id = play_row["gameId"]
    play_id = play_row["playId"]
    target_x = play_row.get("targetX", np.nan)
    target_y = play_row.get("targetY", np.nan)
    defensive_team = play_row.get("defensiveTeam", "")

    if np.isnan(target_x) or np.isnan(target_y):
        return False

    play_tracking = tracking_df[(tracking_df["gameId"] == game_id) & (tracking_df["playId"] == play_id)]
    pass_arrived = play_tracking[play_tracking["event"] == "pass_arrived"]
    if pass_arrived.empty:
        return False

    defenders = pass_arrived[pass_arrived["club"] == defensive_team]
    if defenders.empty:
        return False

    distances = np.sqrt((defenders["x"] - target_x)**2 + (defenders["y"] - target_y)**2)
    return distances.min() > 5

def defenders_shifted_count(play_row, player_play_df):
    game_id = play_row["gameId"]
    play_id = play_row["playId"]
    relevant_players = player_play_df[(player_play_df["gameId"] == game_id) & (player_play_df["playId"] == play_id)]
    return relevant_players["shiftSinceLineset"].sum()

def presnap_motion_confused(play_row, player_play_df):
    game_id = play_row["gameId"]
    play_id = play_row["playId"]
    relevant_players = player_play_df[(player_play_df["gameId"] == game_id) & (player_play_df["playId"] == play_id)]
    return relevant_players["motionSinceLineset"].sum() > 2

def direction_std_high(play_row, tracking_df):
    game_id = play_row["gameId"]
    play_id = play_row["playId"]
    defensive_team = play_row.get("defensiveTeam", "")
    play_tracking = tracking_df[(tracking_df["gameId"] == game_id) & (tracking_df["playId"] == play_id)]
    snap_time = play_tracking[play_tracking["event"] == "ball_snap"]["time"].min()

    if pd.isna(snap_time):
        return False

    post_snap = play_tracking[(play_tracking["time"] > snap_time) & (play_tracking["club"] == defensive_team)]
    if post_snap.empty:
        return False

    return post_snap["dir"].std() > 50

def yard_gained(play_row):
    if play_row.get("yardsGained", 10) > 0:
        return True
    return False

def defense_motion_count(play_row, player_play_df):
    game_id = play_row["gameId"]
    play_id = play_row["playId"]
    defensive_team = play_row.get("defensiveTeam", "")
    relevant_players = player_play_df[
        (player_play_df["gameId"] == game_id) &
        (player_play_df["playId"] == play_id) &
        (player_play_df["teamAbbr"] == defensive_team)
    ]
    return relevant_players["inMotionAtBallSnap"].sum()

def get_confusion_score(play_row, tracking_df, player_play_df):
    score = 0
    if receiver_is_wide_open(play_row, tracking_df): score += 2
    if yard_gained(play_row): score += 2
    if defenders_shifted_count(play_row, player_play_df) > 3: score += 1
    if presnap_motion_confused(play_row, player_play_df): score += 1
    if direction_std_high(play_row, tracking_df): score += 1
    if play_row.get("expectedPointsAdded", 0) > 4: score += 1
    if defense_motion_count(play_row, player_play_df) > 4: score += 1
    return score

def label_confused_play(play_row, tracking_df, player_play_df, threshold=3):
    score = get_confusion_score(play_row, tracking_df, player_play_df)
    return int(score >= threshold)


def label_all_plays(play_df, tracking_df, player_play_df, threshold=3):
    play_df["isConfusedPlay"] = play_df.apply(
        lambda row: label_confused_play(row, tracking_df, player_play_df, threshold), axis=1
    )
    play_df = play_df[['gameId', 'playId', 'isConfusedPlay']].copy()
    
    return play_df

if __name__ == "__main__":
    # Load data
    print("Loading data...")
    play_df = pd.read_csv("/home/tun62034/fuadhassan/nfl-data-bowl/Sample_Data/Raw/plays.csv")
    tracking_df = pd.read_csv("/home/tun62034/fuadhassan/nfl-data-bowl/Sample_Data/Raw/tracking_week_1.csv")
    player_play_df = pd.read_csv("/home/tun62034/fuadhassan/nfl-data-bowl/Sample_Data/Raw/player_play.csv")
    print("Data loaded.")
    print("Processing data...")
    labeled_df = label_all_plays(play_df, tracking_df, player_play_df)
    labeled_df.to_parquet("/home/tun62034/fuadhassan/nfl-data-bowl/Sample_Data/For_Modeling/scoring_system.parquet", index=False)
    print("Data processed and saved.")

