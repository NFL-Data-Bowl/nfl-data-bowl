import pandas as pd

def categorize_yard_gain(yards_gained):
    if yards_gained <= 0:
        return 0  # Bad/No gain or loss
    elif yards_gained <= 8:
        return 0.5  # Normal gain
    else:
        return 1  # Great gain (Defense confused)

def is_play_confused(game_id, play_id):
    """
    Determines whether a play is confused based on yards gained and EPA. (Percentile-based split)

    Args:
    - game_id (int): The game ID.
    - play_id (int): The play ID.

    Returns:
    - yards_gained <= 0: Bad (loss or no gain).
    - 0 < yards_gained <= 8: Normal (within 25%-75%).
    - yards_gained > 8: Great/Confused Defense.
    """

    play = plays[(plays["gameId"] == game_id) & (plays["playId"] == play_id)]
    
    if play.empty:
        print(f"Play (Game {game_id}, Play {play_id}) not found!")
        return None 
    
    yards_gained = categorize_yard_gain(play["yardsGained"].values[0])
    
    return yards_gained
    

if __name__ == "__main__":
    plays = pd.read_csv("/home/tun62034/fuadhassan/nfl-data-bowl/Sample_Data/Raw/plays.csv")
    
    plays["isConfused"] = plays.apply(lambda row: is_play_confused(row["gameId"], row["playId"]), axis=1)
    
    df = plays[["gameId", "playId", "isConfused"]]
    print(df['isConfused'].value_counts())
    df.to_csv("/home/tun62034/fuadhassan/nfl-data-bowl/Sample_Data/Processed/ConfusedPlays.csv", index=False)