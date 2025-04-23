import pandas as pd
import glob
import os
import os
import sys
import warnings
warnings.filterwarnings("ignore")
base_dir = '/home/tun62034/fuadhassan/nfl-data-bowl/'
data_dir_raw = os.path.join(base_dir, 'Sample_Data/Raw')
data_dir_processed = os.path.join(base_dir, 'Sample_Data/Processed')
data_dir_for_modeling = os.path.join(base_dir, 'Sample_Data/For_Modeling')
sys.path.append(base_dir)
sys.path.append(data_dir_raw)
sys.path.append(data_dir_for_modeling)


def frame_to_nflid(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=['time'])

    # Aggregate features per player per play
    agg_df = df.groupby(['gameId', 'playId', 'nflId', 'displayName', 'club']).agg({
        's': ['mean', 'max', 'min'],
        'a': ['mean', 'max', 'min'],
        'dis': ['sum'],
        'x': ['mean', 'std'],
        'y': ['mean', 'std'],
        'o': ['mean'],
        'dir': ['mean'],
        'frameId': ['count'],
    }).reset_index()

    # Flatten column names
    agg_df.columns = ['_'.join(col).strip('_') for col in agg_df.columns]

    agg_df.rename(columns={
        'frameId_count': 'frame_count',
        'dis_sum': 'total_distance',
    }, inplace=True)
    
    agg_df.drop(columns=['displayName', 'club'], inplace=True, errors='ignore')
    
    return agg_df


def player_level_to_play_level(df):

    df['pff_defensiveCoverageAssignment'] = df['pff_defensiveCoverageAssignment'].fillna('OTHER')

    id_cols = ['gameId', 'playId', 'pff_defensiveCoverageAssignment']
    stat_cols = [col for col in df.columns if col not in id_cols + ['nflId', 'teamAbbr']]
    df['nflId'] = df['nflId'].astype(int)  # ensure nflId is preserved

    # Create grouped list of dicts per (gameId, playId, role)
    grouped = (
        df[id_cols + stat_cols + ['nflId']]
        .groupby(['gameId', 'playId', 'pff_defensiveCoverageAssignment'])
        .apply(lambda x: x.drop(columns=['gameId', 'playId', 'pff_defensiveCoverageAssignment']).to_dict('records'))
        .unstack(fill_value=[])
    )
    grouped.reset_index(inplace=True)

    #  Flatten
    flat_df = grouped[['gameId', 'playId']].copy()

    for assignment in grouped.columns:
        if assignment in ['gameId', 'playId']:
            continue
        players_list_col = grouped[assignment]
        
        # Iterate through rows
        max_players = players_list_col.map(len).max()
        
        for i in range(max_players):
            player_i_data = players_list_col.map(lambda players: players[i] if i < len(players) else {})
            player_i_df = pd.json_normalize(player_i_data)
            player_i_df.columns = [f"{assignment}_{i+1}_{col}" for col in player_i_df.columns]
            flat_df = pd.concat([flat_df, player_i_df], axis=1)


    flat_df.fillna(0, inplace=True)

    return flat_df




def main():
    #tracking data
    # Load all tracking data files
    tracking_files = glob.glob(os.path.join(data_dir_raw, 'tracking_week_*.csv'))
    tracking_df = pd.concat((pd.read_csv(file) for file in tracking_files), ignore_index=True) # Add add all
    tracking_df = tracking_df[tracking_df['frameType']=="BEFORE_SNAP"] # keep all before snap data
    tracking_df = frame_to_nflid(tracking_df) # convert to nflId
    
    # Player play data to play and add tracking data

    player_play_df_defense = pd.read_parquet(os.path.join(data_dir_processed,'player_play.parquet'))
    player_play_df_defense_tracking = pd.merge(player_play_df_defense, tracking_df, on=['gameId', 'playId', 'nflId'], how='inner')
    player_play_df_defense_tracking_on_play = player_level_to_play_level(player_play_df_defense_tracking)
    
    # now add play data
    play_df = pd.read_parquet(os.path.join(data_dir_processed,'plays.parquet'))
    player_play_df_defense_tracking_and_play_df_on_play = pd.merge(player_play_df_defense_tracking_on_play, play_df, on=['gameId', 'playId'], how='left', suffixes=('', '_play'))
    player_play_df_defense_tracking_and_play_df_on_play.to_parquet(os.path.join(data_dir_for_modeling,'player_play_defense_tracking_and_play.parquet'), index=False)
    
    
    
    
    

    
    

    

