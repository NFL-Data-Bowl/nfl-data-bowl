import os
import pandas as pd

#function to get any file
def getFile(filepath:str) -> pd.DataFrame:
    full_filepath = os.path.join(os.getcwd(),'nfl-big-data-bowl-2025', filepath)
    return pd.read_csv(full_filepath)

#function to get any play
def getPlaybyId(playId:int) -> pd.DataFrame:
    df= getFile('plays.csv')
    df=df[df['playId']== playId]
    return df

#function to get plays by game
def getPlaybyGame(gameId:int) -> pd.DataFrame:
    df=getFile('plays.csv')
    df=df[df['playId']== gameId]
    return df
    