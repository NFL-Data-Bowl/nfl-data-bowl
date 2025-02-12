import pandas as pd
import numpy as np
import plotly.graph_objects as go

class Visualizer:
    def __init__(self, play_data, players):
        """
        Initialize the Visualizer class.
        
        Parameters:
            play_data (pd.DataFrame): Weekly tracking data containing details for a single play.
            players_file (pd.DataFrame): Player details containing the club, position, and nflId.
        """
        self.play_data = play_data
        self.players = players
    
    def animate_play(self):
        """
        Generate an animation for the provided play data.
        
        Returns:
            go.Figure: A Plotly figure with animation.
        """
        colors = {
            'ARI': "#97233F", 'ATL': "#A71930", 'BAL': '#241773', 'BUF': "#00338D", 'CAR': "#0085CA", 'CHI': "#C83803", 
            'CIN': "#FB4F14", 'CLE': "#311D00", 'DAL': '#003594', 'DEN': "#FB4F14", 'DET': "#0076B6", 'GB': "#203731", 
            'HOU': "#03202F", 'IND': "#002C5F", 'JAX': "#9F792C", 'KC': "#E31837", 'LA': "#003594", 'LAC': "#0080C6", 
            'LV': "#000000", 'MIA': "#008E97", 'MIN': "#4F2683", 'NE': "#002244", 'NO': "#D3BC8D", 'NYG': "#0B2265", 
            'NYJ': "#125740", 'PHI': "#004C54", 'PIT': "#FFB612", 'SEA': "#69BE28", 'SF': "#AA0000", 'TB': '#D50A0A', 
            'TEN': "#4B92DB", 'WAS': "#5A1414", 'football': '#CBB67C'
        }
        
        game_id = self.play_data['gameId'].iloc[0]
        play_id = self.play_data['playId'].iloc[0]
        selected_tracking_df = pd.merge(self.play_data, self.players, how="left", on=["nflId", "displayName"])
        print(selected_tracking_df.columns)
        
        sorted_frame_list = np.sort(selected_tracking_df.frameId.unique())
        
        updatemenus_dict = [{
            "buttons": [
                {"args": [None, {"frame": {"duration": 100, "redraw": False}, "fromcurrent": True}], "label": "Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}], "label": "Pause", "method": "animate"}
            ],
            "direction": "left", "pad": {"r": 10, "t": 87}, "showactive": False, "type": "buttons", "x": 0.1, "xanchor": "right", "y": 0, "yanchor": "top"
        }]
        
        sliders_dict = {
            "active": 0, "yanchor": "top", "xanchor": "left", "currentvalue": {"font": {"size": 20}, "prefix": "Frame:"},
            "transition": {"duration": 300, "easing": "cubic-in-out"}, "pad": {"b": 10, "t": 50}, "len": 0.9, "x": 0.1, "y": 0, "steps": []
        }
        
        frames = []
        for frameId in sorted_frame_list:
            data = []
            for club in selected_tracking_df.club.unique():
                plot_df = selected_tracking_df[(selected_tracking_df.club == club) & (selected_tracking_df.frameId == frameId)].copy()
                if club != "football":
                    hover_text = [f"Id:{row.nflId}<br>Name:{row.displayName}<br>Pos:{row.club}" for _, row in plot_df.iterrows()]
                    data.append(go.Scatter(x=plot_df.x, y=plot_df.y, mode='markers', marker_color=colors[club], name=club, hovertext=hover_text, hoverinfo="text"))
                else:
                    data.append(go.Scatter(x=plot_df.x, y=plot_df.y, mode='markers', marker_color=colors[club], name=club, hoverinfo='none'))
            frames.append(go.Frame(data=data, name=str(frameId)))
            sliders_dict["steps"].append({"args": [[frameId], {"frame": {"duration": 100, "redraw": False}, "mode": "immediate"}], "label": str(frameId), "method": "animate"})
        
        layout = go.Layout(
            autosize=False, width=1200, height=600, xaxis=dict(range=[0, 120], showticklabels=False),
            yaxis=dict(range=[0, 53.3], showgrid=False, showticklabels=False), plot_bgcolor='#00B140',
            title=f"GameId: {game_id}, PlayId: {play_id}", updatemenus=updatemenus_dict, sliders=[sliders_dict]
        )
        
        fig = go.Figure(data=frames[0].data, layout=layout, frames=frames[1:])
        return fig
