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
    return vls, omp

if __name__ == '__main__':
    vls, omp = load_data(data_dir)
    
    combine = vls.merge(omp, on=['gameId','playId'], how='inner')
    
    print(combine.head().T)