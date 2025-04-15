import pandas as pd
from tqdm import tqdm  

games = pd.read_csv("~/nfl-data-bowl/Sample_Data/Raw/games.csv")
plays = pd.read_csv("~/nfl-data-bowl/Sample_Data/Raw/plays.csv")
players = pd.read_csv("~/nfl-data-bowl/Sample_Data/Raw/players.csv")
player_play = pd.read_csv("~/nfl-data-bowl/Sample_Data/Raw/player_play.csv")

weeks = {}
for i in range(1, 10):
    file_path = f"~/nfl-data-bowl/Sample_Data/Raw/tracking_week_{i}.csv" 
    weeks[i] = pd.read_csv(file_path)

def get_defenders(df, gameID, playID, team):
    filtered_df = df[(df['gameId'] == gameID) & 
                     (df['playId'] == playID) & 
                     (df['teamAbbr'] != team)]
    return filtered_df['nflId'].tolist()

def analyze_defensive_movement_through_snap(game_id, play_id, tracking_data, plays, player_play, frame_window=5, speed_threshold=1.0):
    play_info = plays[(plays['gameId'] == game_id) & (plays['playId'] == play_id)]
    if play_info.empty:
        return None, None, None

    offensive_team = play_info['possessionTeam'].values[0]

    defenders = get_defenders(player_play, game_id, play_id, offensive_team)

    play_data = tracking_data[(tracking_data['gameId'] == game_id) & (tracking_data['playId'] == play_id)]
    if play_data.empty:
        return None, None, None

    snap_frame = play_data[play_data['frameType'] == 'SNAP']['frameId'].min()
    if pd.isna(snap_frame):
        return None, None, None

    frames_to_check = list(range(snap_frame - 5, snap_frame + 6))

    defender_data = play_data[(play_data['nflId'].isin(defenders)) & (play_data['frameId'].isin(frames_to_check))]

    if defender_data.empty:
        return 0, 0.0, 0.0

    defenders_moving_through_snap = []
    for nfl_id, player_frames in defender_data.groupby('nflId'):
        if all(player_frames['s'] > speed_threshold):
            defenders_moving_through_snap.append(nfl_id)

    num_movers = len(defenders_moving_through_snap)

    if num_movers == 0:
        return 0, 0.0, 0.0

    snap_data = play_data[(play_data['frameId'] == snap_frame) & (play_data['nflId'].isin(defenders_moving_through_snap))]
    average_snap_speed = snap_data['s'].mean()

    defender_window_data = defender_data[defender_data['nflId'].isin(defenders_moving_through_snap)]
    max_speed = defender_window_data['s'].max()

    return num_movers, average_snap_speed, max_speed

def generate_defender_motion_table(plays, player_play, weeks, frame_window=5, speed_threshold=1.5):
    results = []

    for i in range(1, 10):
        tracking_data = weeks[i]

        for idx, play_row in plays.iterrows():
            game_id = play_row['gameId']
            play_id = play_row['playId']

            if game_id not in tracking_data['gameId'].values:
                continue

            num_defenders, avg_snap_speed, max_speed = analyze_defensive_movement_through_snap(
                game_id, play_id, tracking_data, plays, player_play,
                frame_window=frame_window, speed_threshold=speed_threshold
            )

            if num_defenders is not None:
                results.append({
                    'gameId': game_id,
                    'playId': play_id,
                    'num_defenders_moving': num_defenders,
                    'average_snap_speed': avg_snap_speed,
                    'max_speed_in_window': max_speed
                })

    return pd.DataFrame(results)

game_to_week = {}
for i in range(1, 10):
    week_data = weeks[i]
    for game_id in week_data['gameId'].unique():
        game_to_week[game_id] = i

tracking_game_ids = set(game_to_week.keys())
plays = plays[plays['gameId'].isin(tracking_game_ids)]

results = []

for _, row in tqdm(plays.iterrows(), total=len(plays)):
    gameID = row["gameId"]
    playID = row["playId"]

    week_num = game_to_week.get(gameID)
    if week_num is None:
        continue

    tracking_week = weeks[week_num]

    num_defenders, avg_snap_speed, max_speed = analyze_defensive_movement_through_snap(
        gameID, playID, tracking_week, plays, player_play
    )

    if num_defenders is None:
        continue

    play_stats = {
        "gameID": gameID,
        "playID": playID,
        "num_defenders_moving": num_defenders,
        "average_snap_speed": avg_snap_speed,
        "max_speed_in_window": max_speed
    }

    results.append(play_stats)

final_df = pd.DataFrame(results)
final_df.to_csv("~/nfl-data-bowl/Sample_Data/Raw/motion_through_snap.csv", index=False)

print("✅ Processed plays saved to 'processed_defensive_motion_plays.csv'")
