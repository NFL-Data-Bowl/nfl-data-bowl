def is_play_confused(game_id, play_id):
    """
    Determines whether a play is confused based on yards gained and EPA.

    Args:
    - game_id (int): The game ID.
    - play_id (int): The play ID.

    Returns:
    - int: 1 if confused, 0 if not confused, None if play not found.
    """

    play = plays[(plays["gameId"] == game_id) & (plays["playId"] == play_id)]
    
    if play.empty:
        print(f"Play (Game {game_id}, Play {play_id}) not found!")
        return None 
    
    yards_gained = play["yardsGained"].values[0]

    if yards_gained >= 20:
        return 1  #Confused
    elif yards_gained <= 5:
        return 0  #Not confused
    else:
        return None 