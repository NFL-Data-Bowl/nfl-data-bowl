import pandas as pd
import numpy as np

# How I'm naming the files
'''
games = pd.read_csv("~/nfl-data-bowl/Sample_Data/Raw/games.csv")
plays = pd.read_csv("~/nfl-data-bowl/Sample_Data/Raw/plays.csv")
players = pd.read_csv("~/nfl-data-bowl/Sample_Data/Raw/players.csv")
player_play = pd.read_csv("~/nfl-data-bowl/Sample_Data/Raw/player_play.csv")

weeks = {}
for i in range(1, 10):
    file_path = f"~/nfl-data-bowl/Sample_Data/Raw/tracking_week_{i}.csv" 
    weeks[i] = pd.read_csv(file_path)
'''

def players_in_motion_and_coverage(player_play_df, plays_df, games_df, gameID, playID):
    """
    Get players in motion and their coverage type for a given game and play.

    Parameters:
    player_play_df (pd.DataFrame): DataFrame containing player_play data.
    plays_df (pd.DataFrame): DataFrame containing plays data.
    games_df (pd.DataFrame): DataFrame containing games data.
    gameID (int): The game ID.
    playID (int): The play ID.

    Returns:
    tuple: List of player IDs, coverage type, team abbreviation, and week.
    """
    merged_df = player_play_df.merge(plays_df, on=['gameId', 'playId'], how='inner') \
                              .merge(games_df, on='gameId', how='inner')

    zone_motion_df = merged_df[
        (merged_df['gameId'] == gameID) &
        (merged_df['playId'] == playID) &
        (merged_df['motionSinceLineset'] == 1) &
        (merged_df['pff_manZone'] == 'Zone')
    ]

    if not zone_motion_df.empty:
        return (
            zone_motion_df['nflId'].tolist(),
            zone_motion_df['pff_manZone'].iloc[0],
            zone_motion_df['teamAbbr'].iloc[0],
            zone_motion_df['week'].iloc[0]
        )

    man_motion_df = merged_df[
        (merged_df['gameId'] == gameID) &
        (merged_df['playId'] == playID) &
        (merged_df['motionSinceLineset'] == 1) &
        (merged_df['pff_manZone'] == 'Man')
    ]

    if not man_motion_df.empty:
        return (
            man_motion_df['nflId'].tolist(),
            man_motion_df['pff_manZone'].iloc[0],
            man_motion_df['teamAbbr'].iloc[0],
            man_motion_df['week'].iloc[0]
        )

    return [], None, None, None  

def get_motion_segments(tracking_df, game_id, play_id, player_id, velocity_threshold=2, peak_difference_threshold=0.5):
    """
    Identifies motion start and end frames using peak velocity detection, ignoring small movements.

    Args:
    - tracking_df (DataFrame): Tracking data containing velocity (s) and frameId.
    - game_id (int): Game ID.
    - play_id (int): Play ID.
    - player_id (int): Player ID (offensive motion player).
    - velocity_threshold (float): Squared velocity threshold to detect motion.
    - peak_difference_threshold (float): Ratio to determine if a second peak is significant.

    Returns:
    - List of (motion_start, motion_end) tuples.
    """

    player_tracking = tracking_df[
        (tracking_df['gameId'] == game_id) & 
        (tracking_df['playId'] == play_id) & 
        (tracking_df['nflId'] == player_id) &
        (tracking_df['frameType'] == 'BEFORE_SNAP')
    ].sort_values(by="frameId").reset_index(drop=True)

    if player_tracking.empty:
        print("⚠️ No data found for this player in the given play!")
        return []

    player_tracking['velocity_squared'] = player_tracking['s'] ** 2
    
    total_frames = player_tracking['frameId'].max()

    start_frame = int(total_frames * .33) - 1

    valid_tracking = player_tracking[player_tracking['frameId'] >= start_frame]

    primary_peak_idx = valid_tracking['velocity_squared'].idxmax()
    
    primary_peak_val = valid_tracking.loc[primary_peak_idx, 'velocity_squared']
    
    peak_frame = valid_tracking.loc[primary_peak_idx, 'frameId']

    player_tracking.set_index("frameId", inplace=True)

    motion_start = valid_tracking['frameId'].min()

    motion_end = valid_tracking['frameId'].max()

    for i in range(primary_peak_idx, -1, -1):
        if(i == start_frame - 1):
            break
        if valid_tracking.loc[i, 'velocity_squared'] < velocity_threshold:
            motion_start = valid_tracking.loc[i, 'frameId']
            break
    
    for i in range(primary_peak_idx, motion_end):
        if valid_tracking.loc[i, 'velocity_squared'] < velocity_threshold:
            motion_end = valid_tracking.loc[i, 'frameId']
            break    

    motion_segments = [(int(motion_start), int(motion_end))]

    remaining_tracking = valid_tracking[
        (valid_tracking['frameId'] < motion_start) | (valid_tracking['frameId'] > motion_end)
    ]

    if not remaining_tracking.empty:
        secondary_peak_idx = remaining_tracking['velocity_squared'].idxmax()
        secondary_peak_val = remaining_tracking.loc[secondary_peak_idx, 'velocity_squared']

        if secondary_peak_val >= primary_peak_val * peak_difference_threshold:
            peak_frame_2 = remaining_tracking.loc[secondary_peak_idx, 'frameId']

            motion_start_2, motion_end_2 = valid_tracking['frameId'].min(), valid_tracking['frameId'].max()

            for i in range(secondary_peak_idx, -1, -1):
                 if(i == start_frame - 1):
                    break
                 if valid_tracking.loc[i, 'velocity_squared'] < velocity_threshold:
                    motion_start_2 = valid_tracking.loc[i, 'frameId']
                    break

            for i in range(secondary_peak_idx, motion_end_2):
                if valid_tracking.loc[i, 'velocity_squared'] < velocity_threshold:
                    motion_end_2 = valid_tracking.loc[i, 'frameId']
                    break

            motion_segments.append((int(motion_start_2), int(motion_end_2)))

    return motion_segments

def get_defenders(df, gameID, playID, team):
    """
    Get defenders for a specific game and play.

    Parameters:
    df (pd.DataFrame): DataFrame containing player_play data.
    gameID (int): The game ID.
    playID (int): The play ID.
    team (str): The offensive team abbreviation.

    Returns:
    list: List of defender NFL IDs.
    """
    filtered_df = df[(df['gameId'] == gameID) & 
                     (df['playId'] == playID) & 
                     (df['teamAbbr'] != team)]
    
    return filtered_df['nflId'].tolist()

def calculate_defensive_similarity_with_movement_penalty(df, game_id, play_id, offense_player_id, defense_player_ids, start_frame, end_frame, alpha_distance=0.05, beta_movement=0.05):
    """
    Computes the average reaction score based on cosine similarity, distance change, and movement penalty.

    Args:
    - df (DataFrame): Tracking data containing velocity (s), direction (dir), and position (x, y).
    - game_id (int): Game identifier.
    - play_id (int): Play identifier.
    - offense_player_id (int): The motioning offensive player's ID.
    - defense_player_ids (list): List of defensive player IDs.
    - start_frame (int): Frame to start extracting data.
    - end_frame (int): Frame to stop extracting data.
    - alpha_distance (float): Weight for distance factor.
    - beta_movement (float): Weight for movement penalty.

    Returns:
    - best_defender_id (int): The defensive player ID with the highest reaction score.
    - defender_scores (dict): Dictionary mapping each defender ID to their final score.
    """

    # Filter data for the given play and frame range
    play_data = df[
        (df["gameId"] == game_id) & 
        (df["playId"] == play_id) & 
        (df["frameId"] >= start_frame) & 
        (df["frameId"] <= end_frame)
    ]

    # Extract offensive player's motion data
    offense_data = play_data[play_data["nflId"] == offense_player_id]
    if offense_data.empty:
        print("No offensive player data found in this range!")
        return None, {}

    # Store offensive player (x, y) positions
    offense_positions = {frame: (row["x"], row["y"]) for frame, row in offense_data.set_index("frameId").iterrows()}

    defender_scores = {def_id: [] for def_id in defense_player_ids}
    defender_distance_changes = {}
    defender_movements = {}

    # Iterate through each defensive player
    for def_id in defense_player_ids:
        defense_data = play_data[play_data["nflId"] == def_id]

        if defense_data.empty:
            print(f"No data found for defender {def_id}, skipping.")
            continue

        # Store defender (x, y) positions
        defense_positions = {frame: (row["x"], row["y"]) for frame, row in defense_data.set_index("frameId").iterrows()}

        # Compute distance change
        if start_frame in offense_positions and end_frame in offense_positions and start_frame in defense_positions and end_frame in defense_positions:
            start_off_x, start_off_y = offense_positions[start_frame]
            end_off_x, end_off_y = offense_positions[end_frame]

            start_def_x, start_def_y = defense_positions[start_frame]
            end_def_x, end_def_y = defense_positions[end_frame]

            dist_start = np.sqrt((start_off_x - start_def_x) ** 2 + (start_off_y - start_def_y) ** 2)
            dist_end = np.sqrt((end_off_x - end_def_x) ** 2 + (end_off_y - end_def_y) ** 2)

            defender_distance_changes[def_id] = abs(dist_start - dist_end)

            # Compute total movement of the defender
            defender_movements[def_id] = np.sqrt((end_def_x - start_def_x) ** 2 + (end_def_y - start_def_y) ** 2)

        # Loop through each frame to calculate cosine similarity
        for frame in offense_positions.keys():
            if frame in defense_positions:
                V_x1 = offense_data.loc[offense_data["frameId"] == frame, "s"].values[0] * np.cos(np.radians(offense_data.loc[offense_data["frameId"] == frame, "dir"].values[0]))
                V_y1 = offense_data.loc[offense_data["frameId"] == frame, "s"].values[0] * np.sin(np.radians(offense_data.loc[offense_data["frameId"] == frame, "dir"].values[0]))

                V_x2 = defense_data.loc[defense_data["frameId"] == frame, "s"].values[0] * np.cos(np.radians(defense_data.loc[defense_data["frameId"] == frame, "dir"].values[0]))
                V_y2 = defense_data.loc[defense_data["frameId"] == frame, "s"].values[0] * np.sin(np.radians(defense_data.loc[defense_data["frameId"] == frame, "dir"].values[0]))

                # Compute cosine similarity
                dot_product = (V_x1 * V_x2) + (V_y1 * V_y2)
                mag1 = np.sqrt(V_x1**2 + V_y1**2)
                mag2 = np.sqrt(V_x2**2 + V_y2**2)
                cosine_sim = dot_product / (mag1 * mag2) if mag1 > 0 and mag2 > 0 else 0

                # Store cosine similarity score
                defender_scores[def_id].append(cosine_sim)

    # Normalize distance changes
    max_distance_change = max(defender_distance_changes.values(), default=1)
    for def_id in defender_distance_changes:
        defender_distance_changes[def_id] = 1 - (defender_distance_changes[def_id] / max_distance_change)

    # Normalize defender movement
    max_defender_movement = max(defender_movements.values(), default=1)
    for def_id in defender_movements:
        defender_movements[def_id] = defender_movements[def_id] / max_defender_movement  # Higher is better

    # Compute final scores
    final_scores = {
        def_id: np.mean(scores) + alpha_distance * defender_distance_changes.get(def_id, 0) - beta_movement * (1 - defender_movements.get(def_id, 0))
        for def_id, scores in defender_scores.items()
    }

    # Identify best defender
    best_defender_id = max(final_scores, key=final_scores.get) if final_scores else None

    #print(f"Best defender: {best_defender_id} (Final score)")
    return best_defender_id, final_scores

def calculate_defensive_similarity_zone(df, game_id, play_id, offense_player_id, defense_player_ids, start_frame, end_frame, alpha_distance=0.0, beta_movement=0.3):
    """
    Computes the reaction score based on cosine similarity, distance change, and movement penalty for multiple defenders in a zone play.

    Args:
    - df (DataFrame): Tracking data containing velocity (s), direction (dir), and position (x, y).
    - game_id (int): Game identifier.
    - play_id (int): Play identifier.
    - offense_player_id (int): The motioning offensive player's ID.
    - defense_player_ids (list): List of defensive player IDs.
    - start_frame (int): Frame to start extracting data.
    - end_frame (int): Frame to stop extracting data.
    - alpha_distance (float): Weight for distance factor.
    - beta_movement (float): Weight for movement penalty.

    Returns:
    - best_defenders (list): List of defensive player IDs that reacted to motion across different segments.
    - segment_scores (dict): Dictionary mapping each segment to the top defender.
    """

    # Filter data for the given play and frame range
    play_data = df[
        (df["gameId"] == game_id) & 
        (df["playId"] == play_id) & 
        (df["frameId"] >= start_frame) & 
        (df["frameId"] <= end_frame)
    ]

    # Extract offensive player's motion data
    offense_data = play_data[play_data["nflId"] == offense_player_id]
    if offense_data.empty:
        print("No offensive player data found in this range!")
        return None, {}

    # Store offensive player (x, y) positions
    offense_positions = {frame: (row["x"], row["y"]) for frame, row in offense_data.set_index("frameId").iterrows()}

    # **Break play into 3 segments**
    segment_length = (end_frame - start_frame) // 3
    segments = [
        (start_frame, start_frame + segment_length),
        (start_frame + segment_length + 1, start_frame + 2 * segment_length),
        (start_frame + 2 * segment_length + 1, end_frame)
    ]

    segment_top_defender = {}

    # **Iterate through each segment**
    for seg_idx, (seg_start, seg_end) in enumerate(segments):
        segment_scores = {}
        defender_distance_changes = {}
        defender_movements = {}

        #Iterate through each defensive player
        for def_id in defense_player_ids:
            defense_data = play_data[play_data["nflId"] == def_id]

            if defense_data.empty:
                print(f"No data found for defender {def_id}, skipping.")
                continue

            #Store defender (x, y) positions
            defense_positions = {frame: (row["x"], row["y"]) for frame, row in defense_data.set_index("frameId").iterrows()}

            #Compute distance change
            if seg_start in offense_positions and seg_end in offense_positions and seg_start in defense_positions and seg_end in defense_positions:
                start_off_x, start_off_y = offense_positions[seg_start]
                end_off_x, end_off_y = offense_positions[seg_end]

                start_def_x, start_def_y = defense_positions[seg_start]
                end_def_x, end_def_y = defense_positions[seg_end]

                dist_start = np.sqrt((start_off_x - start_def_x) ** 2 + (start_off_y - start_def_y) ** 2)
                dist_end = np.sqrt((end_off_x - end_def_x) ** 2 + (end_off_y - end_def_y) ** 2)

                defender_distance_changes[def_id] = abs(dist_start - dist_end)

                #Compute total movement of the defender
                defender_movements[def_id] = np.sqrt((end_def_x - start_def_x) ** 2 + (end_def_y - start_def_y) ** 2)

            #Loop through each frame to calculate cosine similarity
            frame_scores = []
            for frame in range(seg_start, seg_end + 1):
                if frame in offense_positions and frame in defense_positions:
                    V_x1 = offense_data.loc[offense_data["frameId"] == frame, "s"].values[0] * np.cos(np.radians(offense_data.loc[offense_data["frameId"] == frame, "dir"].values[0]))
                    V_y1 = offense_data.loc[offense_data["frameId"] == frame, "s"].values[0] * np.sin(np.radians(offense_data.loc[offense_data["frameId"] == frame, "dir"].values[0]))

                    V_x2 = defense_data.loc[defense_data["frameId"] == frame, "s"].values[0] * np.cos(np.radians(defense_data.loc[defense_data["frameId"] == frame, "dir"].values[0]))
                    V_y2 = defense_data.loc[defense_data["frameId"] == frame, "s"].values[0] * np.sin(np.radians(defense_data.loc[defense_data["frameId"] == frame, "dir"].values[0]))

                    #Compute cosine similarity
                    dot_product = (V_x1 * V_x2) + (V_y1 * V_y2)
                    mag1 = np.sqrt(V_x1**2 + V_y1**2)
                    mag2 = np.sqrt(V_x2**2 + V_y2**2)
                    cosine_sim = dot_product / (mag1 * mag2) if mag1 > 0 and mag2 > 0 else 0

                    frame_scores.append(cosine_sim)

            #Compute average similarity for this defender in the segment
            if frame_scores:
                avg_cosine_similarity = np.mean(frame_scores)

                #Normalize distance changes
                max_distance_change = max(defender_distance_changes.values(), default=1)
                norm_distance = 1 - (defender_distance_changes.get(def_id, 0) / max_distance_change) if max_distance_change > 0 else 0

                max_defender_movement = max(defender_movements.values(), default=1)
                norm_movement = defender_movements.get(def_id, 0) / max_defender_movement if max_defender_movement > 0 else 0

                #Compute final segment score
                final_score = avg_cosine_similarity + alpha_distance * norm_distance - beta_movement * (1 - norm_movement)

                segment_scores[def_id] = final_score

        #Identify top defender for this segment
        if segment_scores:
            best_def_id = max(segment_scores, key=segment_scores.get)
            segment_top_defender[seg_idx] = (best_def_id, segment_scores[best_def_id])  # Store as tuple (ID, score)

            # **Print similarity score for the top defender**
            #print(f"🔍 Segment {seg_idx + 1} | Best Defender: {best_def_id} | Cosine Similarity: {segment_scores[best_def_id]:.4f}")

    # Get all unique defenders involved
    best_defenders_with_scores = list(segment_top_defender.values())  # Already (ID, score) format

    #print(f"🛡️ Best defenders across segments: {best_defenders_with_scores}")
    return best_defenders_with_scores 

def get_motion_segments_d(tracking_df, game_id, play_id, player_id, start_frame, end_frame, velocity_threshold=2, peak_difference_threshold=0.5):
    """
    Identifies motion start and end frames using peak velocity detection, ignoring small movements.

    Args:
    - tracking_df (DataFrame): Tracking data containing velocity (s) and frameId.
    - game_id (int): Game ID.
    - play_id (int): Play ID.
    - player_id (int): Player ID (offensive motion player).
    - velocity_threshold (float): Squared velocity threshold to detect motion.
    - peak_difference_threshold (float): Ratio to determine if a second peak is significant.

    Returns:
    - List of (motion_start, motion_end) tuples.
    """

    player_tracking = tracking_df[
        (tracking_df['gameId'] == game_id) & 
        (tracking_df['playId'] == play_id) & 
        (tracking_df['nflId'] == player_id) &
        (tracking_df['frameType'] == 'BEFORE_SNAP')
    ].sort_values(by="frameId").reset_index(drop=True)

    if player_tracking.empty:
        print("No data found for this player in the given play!")
        return []

    player_tracking['velocity_squared'] = player_tracking['s'] ** 2

    valid_tracking = player_tracking[ (player_tracking['frameId'] >= start_frame) | (player_tracking['frameId'] <= end_frame)]

    primary_peak_idx = valid_tracking['velocity_squared'].idxmax()
    
    primary_peak_val = valid_tracking.loc[primary_peak_idx, 'velocity_squared']
    
    peak_frame = valid_tracking.loc[primary_peak_idx, 'frameId']

    player_tracking.set_index("frameId", inplace=True)

    motion_start = valid_tracking['frameId'].min()

    motion_end = valid_tracking['frameId'].max()

    for i in range(primary_peak_idx, -1, -1):
        if(i == start_frame - 1):
            break
        if valid_tracking.loc[i, 'velocity_squared'] < velocity_threshold:
            motion_start = valid_tracking.loc[i, 'frameId']
            break
    
    for i in range(primary_peak_idx, motion_end):
        if valid_tracking.loc[i, 'velocity_squared'] < velocity_threshold:
            motion_end = valid_tracking.loc[i, 'frameId']
            break    
        
    return int(motion_start)


#MAIN FUNCTION
def process_all_plays(gameID, playID):
    segment_switch_count = 0
    num_motions = 0
    num_motion_events = 0
    avg_time_to_react = 0
    max_time_to_react = 0
    num_defenders_react = 0
    avg_sim_score = 0.0
    max_sim_score = 0.0
    var_sim_score = 0.0
    total_motion_duration = 0
    
    motion_data = {}
    filtered_motion_data = {}
    
    nfl_ids, coverage_type, team, week = players_in_motion_and_coverage(player_play, plays, games, gameID, playID)
    
    if nfl_ids == []:
        return {
            "segment_switch_count": segment_switch_count,
            "num_motions": num_motions,
            "num_motion_events": num_motion_events,
            "num_defenders_react": num_defenders_react,
            "avg_sim_score": avg_sim_score,
            "max_sim_score": max_sim_score,
            "var_sim_score": var_sim_score,
            "total_motion_duration": total_motion_duration
        } 
    
    tracking_df = weeks[week]
    
    for nfl_id in nfl_ids:
        motion_segments = get_motion_segments(tracking_df, gameID, playID, nfl_id)
        motion_data[nfl_id] = motion_segments

    for nfl_id, motion_segments in motion_data.items():
        filtered_segments = [(start, end) for start, end in motion_segments if (end - start) >= 15]

        if filtered_segments:
            filtered_motion_data[nfl_id] = filtered_segments
            num_motions += 1
            
    motion_data = filtered_motion_data

    num_motion_events = sum(len(segments) for segments in motion_data.values())
    
    defender_ids = get_defenders(player_play, gameID, playID, team)
    all_similarity_scores = []
    
    if coverage_type == "Man":
        best_defenders = {}  

        for offense_player_id, motion_segments in motion_data.items():
            for start_frame, end_frame in motion_segments:
                best_defender, defender_scores = calculate_defensive_similarity_with_movement_penalty(
                    tracking_df, gameID, playID, offense_player_id, defender_ids, start_frame + 5, end_frame
                )

                if best_defender is not None:
                    best_defenders[offense_player_id] = (best_defender, defender_scores[best_defender])
                    all_similarity_scores.append(defender_scores[best_defender])

        
    if coverage_type == "Zone":
        best_defenders = {}  

        for offense_player_id, motion_segments in motion_data.items():
            segment_defenders = []
            last_defender = None

            for start_frame, end_frame in motion_segments:

                best_defenders_with_scores = calculate_defensive_similarity_zone(
                    tracking_df, gameID, playID, offense_player_id, defender_ids, start_frame + 3, end_frame
                )

                for defender, score in best_defenders_with_scores:
                    segment_defenders.append((defender, score))
                    all_similarity_scores.append(score)

                    if last_defender is not None and last_defender != defender:
                        segment_switch_count += 1
                    last_defender = defender

            if segment_defenders:
                best_defenders[offense_player_id] = segment_defenders

        
    if all_similarity_scores:
        avg_sim_score = np.mean(all_similarity_scores)
        max_sim_score = np.max(all_similarity_scores)
        var_sim_score = np.var(all_similarity_scores)
    
    unique_defenders = set()
    for defenders in best_defenders.values():
        if isinstance(defenders, list):
            unique_defenders.update([d[0] for d in defenders])
        else:  
            unique_defenders.add(defenders[0])

    num_defenders_react = len(unique_defenders)
    
    motion_frames = set()

    for segments in motion_data.values():
        for start, end in segments:
            motion_frames.update(range(start, end + 1)) 

    total_motion_duration = len(motion_frames)

    return {
        "segment_switch_count": segment_switch_count,
        "num_motions": num_motions,
        "num_motion_events": num_motion_events,
        "num_defenders_react": num_defenders_react,
        "avg_sim_score": float(avg_sim_score),
        "max_sim_score": float(max_sim_score),
        "var_sim_score": float(var_sim_score),
        "total_motion_duration": total_motion_duration
    }
    
    
   
# How I'm calling my main function
'''
results = []

for _, row in plays.iterrows():
    gameID = row["gameId"]
    playID = row["playId"]

    play_stats = process_all_plays(gameID, playID)

    play_stats["gameID"] = gameID
    play_stats["playID"] = playID

    results.append(play_stats)

final_df = pd.DataFrame(results)

final_df.to_csv("~/nfl-data-bowl/Sample_Data/Raw/processed_offensive_motion_plays-test.csv", index=False)

print("Processed plays saved to 'processed_plays.csv'")
'''

