# This script generates an animation for a specific play and saves it as a GIF.
# It uses the Plotly library to create the animation and Imageio to save it as a GIF.
# The Visualizer class is initialized with the play data, players data, and plays data.
# The animate_play method generates the animation using the provided data.
# The generate_gif method saves the animation as a GIF file.
# The show_gif method displays the generated GIF inside a notebook.

# Future Work:
# - Add any other visualizations that might be useful for analyzing the play data (e.g., heatmaps, player trajectories) on this script.

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys
import imageio
from IPython.display import display, Image
base_dir = "Your_Base_Directory"
data_dir = os.path.join(base_dir, 'Data')
sys.path.append(base_dir)
from Code.utils.Helper import FrameDataHelper


class Visualizer:
    def __init__(self, week, players, plays):
        """
        initialize the Visualizer class.
        
        parameters:
            week (pd.DataFrame): Weekly tracking data containing details for a single play.
            players (pd.DataFram): Path to the players CSV file.
            plays(pd.DataFram): Path to the plays CSV file.
        """
        self.week = week
        self.players = players
        self.plays = plays
    
    def animate_play(self):
        """
        generate an animation for the provided play data.
        
        returns:
            go.Figure: a plotly figure with animation.
        """
        colors = {
            'football': '#ffeb00'
        }
        
        game_id = self.week['gameId'].iloc[0]
        play_id = self.week['playId'].iloc[0]
        
        # Retrieve necessary data from other files
        selected_play = self.plays[(self.plays['gameId'] == game_id) & (self.plays['playId'] == play_id)]
        selected_players = self.players[self.players['nflId'].isin(self.week['nflId'])]

        
        selected_tracking_df = pd.merge(self.week, selected_players, how="left", on="nflId")
        
        sorted_frame_list = np.sort(selected_tracking_df.frameId.unique())
        
        # Get play general information
        line_of_scrimmage = selected_play.absoluteYardlineNumber.values[0]
        first_down_marker = line_of_scrimmage + selected_play.yardsToGo.values[0]
        down = selected_play.down.values[0]
        quarter = selected_play.quarter.values[0]
        gameClock = selected_play.gameClock.values[0]
        playDescription = selected_play.playDescription.values[0]
        possession_team = selected_play.possessionTeam.iloc[0]
        defensive_team = selected_play.defensiveTeam.iloc[0]
        team_colors = {
            possession_team: "#0001ff",  # Blue for offense
            defensive_team: "#ff0000"  # Red for defense
        }
        selected_tracking_df['teamColor'] = selected_tracking_df['club'].map(team_colors)
        
        # Handle case where we have a really long Play Description and want to split it into two lines
        if len(playDescription.split(" ")) > 15 and len(playDescription) > 115:
            playDescription = " ".join(playDescription.split(" ")[0:16]) + "<br>" + " ".join(playDescription.split(" ")[16:])

        # initialize plotly start and stop buttons for animation
        updatemenus_dict = [
            {
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 100, "redraw": False},
                                    "fromcurrent": True, "transition": {"duration": 0}}],
                        "label": "Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                        "mode": "immediate",
                                        "transition": {"duration": 0}}],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }
        ]
        # initialize plotly slider to show frame position in animation
        sliders_dict = {
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 20},
                "prefix": "Frame:",
                "visible": True,
                "xanchor": "right"
            },
            "transition": {"duration": 300, "easing": "cubic-in-out"},
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": []
        }


        frames = []
        for frameId in sorted_frame_list:
            data = []
            # Add Numbers to Field 
            data.append(
                go.Scatter(
                    x=np.arange(20,110,10), 
                    y=[5]*len(np.arange(20,110,10)),
                    mode='text',
                    text=list(map(str,list(np.arange(20, 61, 10)-10)+list(np.arange(40, 9, -10)))),
                    textfont_size = 30,
                    textfont_family = "Courier New, monospace",
                    textfont_color = "#ffffff",
                    showlegend=False,
                    hoverinfo='none'
                )
            )
            data.append(
                go.Scatter(
                    x=np.arange(20,110,10), 
                    y=[53.5-5]*len(np.arange(20,110,10)),
                    mode='text',
                    text=list(map(str,list(np.arange(20, 61, 10)-10)+list(np.arange(40, 9, -10)))),
                    textfont_size = 30,
                    textfont_family = "Courier New, monospace",
                    textfont_color = "#ffffff",
                    showlegend=False,
                    hoverinfo='none'
                )
            )
            # Add line of scrimage 
            data.append(
                go.Scatter(
                    x=[line_of_scrimmage,line_of_scrimmage], 
                    y=[0,53.5],
                    line_dash='dash',
                    line_color='blue',
                    showlegend=False,
                    hoverinfo='none'
                )
            )
            # Add First down line 
            data.append(
                go.Scatter(
                    x=[first_down_marker,first_down_marker], 
                    y=[0,53.5],
                    line_dash='dash',
                    line_color='yellow',
                    showlegend=False,
                    hoverinfo='none'
                )
            )
            # Plot Players
            for club in selected_tracking_df.club.unique():
                plot_df = selected_tracking_df[(selected_tracking_df.club==club)&(selected_tracking_df.frameId==frameId)].copy()
                if club != "football":
                    hover_text_array=[]
                    for nflId in plot_df.nflId:
                        selected_player_df = plot_df[plot_df.nflId==nflId]
                        hover_text_array.append("nflId:{}<br>displayName:{}<br>Position:{}".format(
                                                            selected_player_df["nflId"].values[0],
                                                            selected_player_df["displayName_y"].values[0],
                                                            selected_player_df["position"].values[0]
                                                        ))
                    data.append(go.Scatter(x=plot_df["x"], y=plot_df["y"],mode = 'markers',marker_color=team_colors.get(club, "#808080"),name=club,hovertext=hover_text_array,hoverinfo="text"))
                else:
                    data.append(go.Scatter(x=plot_df["x"], y=plot_df["y"],mode = 'markers',marker_color=colors[club],name=club,hoverinfo='none'))
            # add frame to slider
            slider_step = {"args": [
                [frameId],
                {"frame": {"duration": 100, "redraw": False},
                "mode": "immediate",
                "transition": {"duration": 0}}
            ],
                "label": str(frameId),
                "method": "animate"}
            sliders_dict["steps"].append(slider_step)
            frames.append(go.Frame(data=data, name=str(frameId)))

        scale=10
        layout = go.Layout(
            autosize=False,
            width=120*scale,
            height=60*scale,
            xaxis=dict(range=[0, 120], autorange=False, tickmode='array',tickvals=np.arange(10, 111, 5).tolist(),showticklabels=False),
            yaxis=dict(range=[0, 53.3], autorange=False,showgrid=False,showticklabels=False),

            plot_bgcolor='#00B140',
            # Create title and add play description at the bottom of the chart for better visual appeal
            title=f"GameId: {game_id}, PlayId: {play_id}<br>{gameClock} {quarter}Q"+"<br>"*19+f"{playDescription}",
            updatemenus=updatemenus_dict,
            sliders = [sliders_dict]
        )

        fig = go.Figure(
            data=frames[0]["data"],
            layout= layout,
            frames=frames[1:]
        )
        # Create First Down Markers 
        for y_val in [0,53]:
            fig.add_annotation(
                    x=first_down_marker,
                    y=y_val,
                    text=str(down),
                    showarrow=False,
                    font=dict(
                        family="Courier New, monospace",
                        size=16,
                        color="black"
                        ),
                    align="center",
                    bordercolor="black",
                    borderwidth=2,
                    borderpad=4,
                    bgcolor="#ff7f0e",
                    opacity=1
                    )

        return fig
        


    def generate_gif(self, output_gif="play_animation.gif"):
        """
        generate a GIF from the animation and save it.

        parameters:
            output_gif (str): File name for the output GIF.

        returns:
            nothing
        """
        fig = self.animate_play()
        temp_folder = "temp_frames"
        os.makedirs(temp_folder, exist_ok=True)
        frame_files = []

        # Extract frames and save them as images
        for i, frame in enumerate(fig.frames):
            frame_path = os.path.join(temp_folder, f"frame_{i}.png")

            # Set the figure's data to the frame's data
            fig.update(data=frame.data)

            # Save frame as an image
            fig.write_image(frame_path)
            frame_files.append(frame_path)

        # Create GIF from saved frames
        images = [imageio.imread(frame) for frame in frame_files]
        imageio.mimsave(output_gif, images, duration=0.1)

        # Cleanup temporary images
        for frame in frame_files:
            os.remove(frame)
        os.rmdir(temp_folder)

        print(f"GIF saved as {output_gif}")

    def show_gif(self, gif_path="play_animation.gif"):
        """
        display the generated GIF inside a notebook.
        
        parameters:
            gif_path (str): File name of the GIF to display.
        
        returns:
            IPython display object: Display the GIF inside a notebook.
        """
        return display(Image(filename=gif_path))
    


# Test the Visualizer
def main():
    print("\nStarting Play Animation Process...\n")

    try:

        print("Loading data files...")
        players = pd.read_csv(os.path.join(data_dir, "players.csv"))
        plays = pd.read_csv(os.path.join(data_dir, "plays.csv"))
        week1 = pd.read_csv(os.path.join(data_dir, "tracking_week_1.csv"))
        print("Data successfully loaded!\n")

        play_focus = 56
        frame_helper = FrameDataHelper(week1)

        print(f"Extracting play data for Game ID: 2022090800, Play ID: {play_focus}...")
        week1_play_56_data = frame_helper.get_play_data(game_id=2022090800, play_id=play_focus)
        print("Play data extraction complete!\n")

        print("Initializing the Visualizer...")
        visualizer = Visualizer(week1_play_56_data, players, plays)
        print("Visualizer initialized!\n")

        print("Generating GIF animation...")
        print("This may take a few seconds...")
        visualizer.generate_gif("play_56.gif")
        print("GIF generated successfully as 'play_56.gif'!\n")

        print("Displaying the generated GIF...")
        visualizer.show_gif("play_56.gif")
        print("GIF displayed!\n")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
