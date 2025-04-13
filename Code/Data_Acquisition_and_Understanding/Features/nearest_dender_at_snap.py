import pandas
class nearest_defender_to_receiver_at_snap:
    def __init__(self, game_id:int, play_id:int):
        self.game_id=game_id
        self.play_id= play_id
        
    def getFeature(self,movement_data:pandas.DataFrame, player_data:pandas.DataFrame):
        nearest_defender_dict={}
        data= movement_data[(movement_data['gameId']==self.game_id) & (movement_data['frameType']=='SNAP') & (movement_data['playId']==self.play_id)]
        data= pandas.merge(data,player_data, how="left", on="nflId")
        
        number=1
        wr_count=(data[data['position']=='WR'].count())
        wr_count=wr_count['gameId']
        
        while number <= wr_count:
            data[f'nearest_defender_{number}']=0
            number+=1

        wide_recievers=data[data['position']=='WR']
        wide_recievers=wide_recievers['displayName_x'].unique()
        nearest_defender_dict,data= self.setDataFeature(data,nearest_defender_dict,wide_recievers)
        return nearest_defender_dict, data
    
    def setDataFeature(self,data:pandas.DataFrame, nearest_defender_dict:dict, wide_recievers):
        number=1
        for wr in wide_recievers:
            min_distance, defensive_player= self.defender_distance_to_wr(wr, data)
            data[f'nearest_defender_{number}']= min_distance
            nearest_defender_dict[wr]= defensive_player
            number+=1
        return nearest_defender_dict,data
    
    def defender_distance_to_wr(self,wide_reciever:str, data:pandas.DataFrame):
        defense_positions=['CB','SS', 'ILB', 'OLB', 'DE', 'DT', 'FS', 'NT', 'LB', 'MLB', 'DB']
        wr_df= data[data["displayName_x"]==wide_reciever]
        wr_x_distance= wr_df.iloc[0,10] #dataframe column position of x
        wr_y_distance= wr_df.iloc[0,11] #dataframe column position of y 
    
        min_distance=10000
        defensive_player= ""
        for index, row in data.iterrows():
            if row["position"] not in defense_positions:
                continue
        
            defender_distance_to_wr= (abs(row['x']-wr_x_distance)) + (abs(row['y']-wr_y_distance))
            if defender_distance_to_wr < min_distance:
                min_distance= defender_distance_to_wr
                defensive_player= row["displayName_x"]
        return min_distance, defensive_player 
