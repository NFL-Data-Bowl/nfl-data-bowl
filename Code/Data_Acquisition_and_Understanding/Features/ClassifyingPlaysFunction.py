import pandas as pd

def is_play_confused(row):
    """
    Determines whether a play is confused based on yards gained and EPA. (Percentile-based split)

    Args:
    - row 

    Returns:
    - epa <= -0.5 or yardsGained <= 2 and EPA < 1 (not confused)
    - yards_gained >= 17 and EPA >= 1.5, or extra condition for 3/4 plays(confused)
    - else normal
    """

    if row['yardsGained'] >= 17 and row['expectedPointsAdded'] >= 1.5:
        return 2 
    elif row['expectedPointsAdded'] >= 2 and row['yardsGained'] >= 10 and row['down'] in [3, 4] and row['yardsToGo'] > 7:
        return 2 
    elif row['expectedPointsAdded'] <= -0.5 or (row['yardsGained'] <= 2 and row['expectedPointsAdded'] < 1):
        return 0 
    else:
        return 1
    

if __name__ == "__main__":
    plays = pd.read_csv("~/nfl-data-bowl/Sample_Data/Raw/plays.csv")
    
    plays = plays[plays['penaltyYards'].isna()]
    
    plays["isConfused"] = plays.apply(is_play_confused, axis=1)
    
    df = plays[["gameId", "playId", "isConfused"]]
    print(df['isConfused'].value_counts())
    df.to_csv("~/nfl-data-bowl/Sample_Data/Raw/playlabels.csv", index=False)