"""
Fuad Hassan
Date: 2025-03-18
Description: This script computes the velocity of late shifts feature.

The class takes defensive player tracking data and computes:
- teamTotalDistance
- totalAverageSpeed
- numPlayerMoved

It groups results by gameId and playId.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

base_dir = '/home/tun62034/fuadhassan/nfl-data-bowl/'
data_dir = os.path.join(base_dir, 'Sample_Data/Raw')
sys.path.append(base_dir)
sys.path.append(data_dir)

from Code.utils.Helper import FrameDataHelper

class VelocityLateShifts:
    def __init__(self, static_data, week_dataframes):
        self.games = static_data['games']
        self.players = static_data['players']
        self.plays = static_data['plays']
        self.player_play = static_data['player_play']
        self.week_dataframes = week_dataframes
        self.result_df = pd.DataFrame()

    def run(self):
        print("[VelocityLateShifts] Running process...")
        self.process_all_weeks()
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

        self.all_weeks_filtered = pd.concat(weekly_results, ignore_index=True)
        print(f"All weeks combined shape: {self.all_weeks_filtered.shape}")

    def preprocess_defensive_plays(self, week_df):
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
        print("Computing metrics...")
        data = self.all_weeks_filtered
        grouped_player = data.groupby(['gameId', 'playId', 'nflId'])
        total_distance = grouped_player['dis'].sum().reset_index(name='totalDistance')
        average_speed = grouped_player['s'].mean().reset_index(name='averageSpeed')
        player_metrics = total_distance.merge(average_speed, on=['gameId', 'playId', 'nflId'])
        moved_players = player_metrics[player_metrics['totalDistance'] > 0]
        team_total_distance = data.groupby(['gameId', 'playId'])['dis'].sum().reset_index(name='teamTotalDistance')
        total_avg_speed = moved_players.groupby(['gameId', 'playId'])['averageSpeed'].sum().reset_index(name='totalAverageSpeed')
        num_players_moved = moved_players.groupby(['gameId', 'playId']).size().reset_index(name='numPlayerMoved')
        result = team_total_distance.merge(total_avg_speed, on=['gameId', 'playId'], how='left')
        result = result.merge(num_players_moved, on=['gameId', 'playId'], how='left')


        result['totalAverageSpeed'] = result['totalAverageSpeed'].fillna(0)
        result['numPlayerMoved'] = result['numPlayerMoved'].fillna(0).astype(int)

        self.result_df = result[['gameId', 'playId', 'teamTotalDistance', 'totalAverageSpeed', 'numPlayerMoved']]
        print(f"Final shape: {self.result_df.shape}")

    def save_processed_data(self, output_dir, filename='velocity_late_shifts_summary.csv'):
        output_path = os.path.join(output_dir, filename)
        self.result_df.to_csv(output_path, index=False)
        print(f"Saved final summary to {output_path}")



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
    vls_result.to_csv('velocity_late_shifts.csv', index=False)

