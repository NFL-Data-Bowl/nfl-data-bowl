"""
Fuad Hassan
Date: 2025-03-18
Description: This script is used to compute the velocity of late shifts feature.

The class takes the datafreames and processe and retuns the dataframe with the velocity of late shifts feature.

example:
       gameId  playId    nflId  totalDistance  teamTotalDistance  averageSpeed  numPlayerMoved
0  2022090800      56  38577.0           0.13               6.35        0.0315               9
1  2022090800      56  41239.0           0.10               6.35        0.0055               9
2  2022090800      56  42816.0           0.48               6.35        0.2370               9
3  2022090800      56  43294.0           1.12               6.35        0.5590               9
4  2022090800      56  43298.0           0.00               6.35        0.0000               9

"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")
base_dir = '/home/user/nfl-data-bowl/'
data_dir = os.path.join(base_dir, 'Sample_Data/Raw')
sys.path.append(base_dir)
sys.path.append(data_dir)

from Code.utils.Helper import FrameDataHelper
from Code.utils.Visualize import Visualizer



class VelocityLateShifts:
    def __init__(self, static_data, week_dataframes):
        """
        takes all data
        """
        self.games = static_data['games']
        self.players = static_data['players']
        self.plays = static_data['plays']
        self.player_play = static_data['player_play']
        self.week_dataframes = week_dataframes
        self.result_df = pd.DataFrame()

    def run(self):
        """ run the entire pipeline """
        print("[VelocityLateShifts] Running process...")

        # Step1: process defensive plays across all weeks
        self.process_all_weeks()

        # Step2: Compute metrics and summarize
        self.compute_and_merge_metrics()

        print("[VelocityLateShifts] Process complete.")
        return self.result_df

    def process_all_weeks(self):
        print("Processing all weeks...")  
        weekly_results = []

        for week_num, week_df in enumerate(self.week_dataframes, start=1):
            print(f"[Week {week_num}] Processing...")

            defense_plays = self.preprocess_defensive_plays(week_df)
            snap_times = self.extract_snap_times(defense_plays)
            filtered_data = self.filter_pre_snap_data(defense_plays, snap_times)

            weekly_results.append(filtered_data)

        all_weeks_filtered = pd.concat(weekly_results, ignore_index=True)
        print(f"All weeks combined shape: {all_weeks_filtered.shape}")
        self.all_weeks_filtered = all_weeks_filtered

    def preprocess_defensive_plays(self, week_df):
        " defensive team info and filter plays for defense "
        team_info = self.plays[['gameId', 'playId', 'possessionTeam', 'defensiveTeam']].drop_duplicates()
        week_with_team_info = week_df.merge(team_info, on=["gameId", "playId"], how="left")
        defense_plays = week_with_team_info[week_with_team_info['club'] == week_with_team_info['defensiveTeam']]
        return defense_plays

    def extract_snap_times(self, defense_plays):
        helper = FrameDataHelper(defense_plays)
        snap_time = helper.extract_frame_data_time("SNAP")
        snap_time.rename(columns={'start_time': 'snap_start_time'}, inplace=True)

        return snap_time[['gameId', 'playId', 'snap_start_time']]

    def filter_pre_snap_data(self, defense_plays, snap_times, seconds_before_snap=2):
        defense_with_snap = defense_plays.merge(snap_times, on=["gameId", "playId"], how="left")

        defense_with_snap['time'] = pd.to_datetime(defense_with_snap['time'], format='mixed')

        mask = (
            (defense_with_snap['time'] >= defense_with_snap['snap_start_time'] - pd.Timedelta(seconds=seconds_before_snap)) &
            (defense_with_snap['time'] < defense_with_snap['snap_start_time'])
        )

        filtered = defense_with_snap[mask].sort_values(by=['gameId', 'playId', 'nflId', 'frameId'])

        return filtered

    def compute_and_merge_metrics(self):
        """ Compute distances, speeds, and other metrics """
        print("Computing metrics on all weeks combined...")

        filtered_data = self.all_weeks_filtered

        grouped_player = filtered_data.groupby(['gameId', 'playId', 'nflId'])
        grouped_play = filtered_data.groupby(['gameId', 'playId'])

        # Total distance per player
        total_distance_per_player = grouped_player['dis'].sum().reset_index(name='totalDistance')

        # Total distance per team per play
        total_distance_per_team = grouped_play['dis'].sum().reset_index(name='teamTotalDistance')

        # Players who moved (distance > 0)
        player_moved = total_distance_per_player[total_distance_per_player['totalDistance'] > 0]
        player_moved_per_play = player_moved.groupby(['gameId', 'playId']).size().reset_index(name='numPlayerMoved')

        # Average speed per player
        avg_speed_per_player = grouped_player['s'].mean().reset_index(name='averageSpeed')

        # Merge everything
        summary = total_distance_per_player.merge(
            avg_speed_per_player, on=['gameId', 'playId', 'nflId'], how='left').merge(total_distance_per_team, on=['gameId', 'playId'], how='left').merge(player_moved_per_play, on=['gameId', 'playId'], how='left')

        summary = summary[['gameId', 'playId', 'nflId', 'totalDistance', 'teamTotalDistance', 'averageSpeed', 'numPlayerMoved']]
        self.result_df = summary

        print(f"Final summary DataFrame shape: {summary.shape}")

    def save_processed_data(self, output_dir, filename='final_summary.csv'):
        """ Save the final dataframe to a CSV """
        output_path = os.path.join(output_dir, filename)
        self.result_df.to_csv(output_path, index=False)
        print(f"Final summary saved at: {output_path}")



if __name__ == "__main__":
    print("Running example...")
    start_time = pd.Timestamp.now()
    static_data = {
        "games": pd.read_csv(f'{data_dir}/games.csv'),
        "players": pd.read_csv(f'{data_dir}/players.csv'),
        "plays": pd.read_csv(f'{data_dir}/plays.csv'),
        "player_play": pd.read_csv(f'{data_dir}/player_play.csv')}
    week_dataframes = [
        pd.read_csv(f'{data_dir}/tracking_week_{i}.csv') for i in range(1, 8)]
    # run example
    end_time = pd.Timestamp.now()
    print(f"Example completed in {end_time - start_time}")
    vls_processor = VelocityLateShifts(static_data, week_dataframes)
    vls_result = vls_processor.run()
    print(vls_result.head())

