import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")
base_dir = '/home/tun62034/fuadhassan/nfl-data-bowl/'
data_dir = os.path.join(base_dir, 'Sample_Data/Processed')
sys.path.append(base_dir)
sys.path.append(data_dir)


def load_data(data_dir):
    vls = pd.read_csv(os.path.join(data_dir, 'velocity_late_shifts.csv'))
    omp = pd.read_csv(os.path.join(data_dir, 'offensive_motion_plays.csv'))
    pts = pd.read_csv(os.path.join(data_dir, 'players_through_snap.csv'))
    target = pd.read_csv(os.path.join(data_dir, 'TargetValueConfusedPlays.csv'))
    
    return vls, omp,pts, target

if __name__ == '__main__':
    vls, omp, pts, target = load_data(data_dir)
    
    combine = vls.merge(omp, on=['gameId','playId'], how='inner')
    combine = combine.merge(pts, on=['gameId','playId'], how='inner')
    combine = combine.merge(target, on=['gameId','playId'], how='inner')
    
    print(combine.head(1).T)
    
    