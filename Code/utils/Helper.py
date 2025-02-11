# contains helper functions for data processing
import pandas as pd

class FrameDataHelper:
    """
    A helper class for processing and extracting frame data from a given dataset.
    """

    def __init__(self, week,):
        """
        Initialize the helper with a dataset.

        Parameters:
            week (pd.DataFrame): The DataFrame containing frame data.
        """
        self.week = week

    @staticmethod
    def convert_to_datetime(time_str):
        """
        Convert a time string to a datetime object.

        Parameters:
            time_str (str): The time string to convert.

        Returns:
            pd.Timestamp: The converted datetime object.
        """
        return pd.to_datetime(time_str)

    def extract_frame_data_time(self, frame_type, game_id=None, play_id=None, df=None):
        """
        Extract the start and end frameId and corresponding time for each play given a frameType.
        Optionally filter by game_id, play_id, and use a custom DataFrame.

        Parameters:
            frame_type (str): The frame type to filter by ('BEFORE_SNAP', 'SNAP', 'AFTER_SNAP').
            game_id (int, optional): The game ID to filter by. If None, returns data for all games.
            play_id (int, optional): The play ID to filter by. If None, returns data for all plays.
            df (pd.DataFrame, optional): The DataFrame to use instead of self.week. If None, defaults to self.week.

        Returns:
            pd.DataFrame: A DataFrame containing gameId, playId, start/end frameId, and corresponding times.
        """
        # Use the provided DataFrame or default to self.week
        frame_data = df if df is not None else self.week

        # Filter by frame_type
        frame_data = frame_data[frame_data['frameType'] == frame_type]

        # If game_id is provided, filter by gameId
        if game_id is not None:
            frame_data = frame_data[frame_data['gameId'] == game_id]

        # If play_id is provided, filter by playId
        if play_id is not None:
            frame_data = frame_data[frame_data['playId'] == play_id]

        # Group by both gameId and playId, and calculate start and end frameId and time
        frame_data = (
            frame_data.groupby(['gameId', 'playId'])[['frameId', 'time']]
            .agg(start=('frameId', 'min'), end=('frameId', 'max'),
                start_time=('time', 'min'), end_time=('time', 'max'))
            .reset_index()
        )

        # Rename columns for clarity
        frame_data.columns = ['gameId', 'playId', 'start_frameId', 'end_frameId', 'start_time', 'end_time']

        # Convert time columns to datetime
        frame_data['start_time'] = frame_data['start_time'].apply(self.convert_to_datetime)
        frame_data['end_time'] = frame_data['end_time'].apply(self.convert_to_datetime)

        return frame_data


    def get_play_data(self, game_id, play_id=None, frame_type=None):
        """
        Retrieve frame data for a given play ID and game ID with an option to filter by frame type.
        If play_id is None, return all plays for the specified gameId.

        Parameters:
            gameId (int): The game ID to filter the data.
            play_id (int, optional): The play ID to filter the data. If None, return all plays for the gameId.
            frame_type (str, optional): The frame type to filter by ('BEFORE_SNAP', 'SNAP', 'AFTER_SNAP').

        Returns:
            pd.DataFrame: The filtered DataFrame containing frame data for the specified play ID and game ID.
        """
        # Filter by gameId
        filtered_data = self.week[self.week['gameId'] == game_id]

        # Further filter by play_id if provided
        if play_id is not None:
            filtered_data = filtered_data[filtered_data['playId'] == play_id]

        # Further filter by frame_type if provided
        if frame_type:
            filtered_data = filtered_data[filtered_data['frameType'] == frame_type]

        return filtered_data