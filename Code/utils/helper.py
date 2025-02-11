# contains helper functions for data processing

def get_play_frame_data(week1, play_id, frame_type=None):
    """
    Retrieve frame data for a given play ID with an option to filter by frame type.
    
    Parameters:
        week1 (pd.DataFrame): The DataFrame containing frame data.
        play_id (int): The play ID to filter the data.
        frame_type (str, optional): The frame type to filter by ('BEFORE_SNAP', 'SNAP', 'AFTER_SNAP').
        
    Returns:
        pd.DataFrame: The filtered DataFrame containing frame data for the specified play ID.
    """
    filtered_data = week1[week1['playId'] == play_id]
    
    if frame_type:
        filtered_data = filtered_data[filtered_data['frameType'] == frame_type]
    
    return filtered_data
