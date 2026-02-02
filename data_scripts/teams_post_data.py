import pandas as pd
import matplotlib.pyplot as plt
from data_scripts import _store_data as sd

def teams_post_wins_percentage():
    team_results = sd.teams_post_df.groupby("tmID")[["W", "L"]].sum().reset_index()

    team_results["Games Played"] = team_results["W"] + team_results["L"]
    team_results["Win %"] = (team_results["W"] / team_results["Games Played"]).round(3)

    sorted_results = team_results.sort_values(by="Win %", ascending=False)

    plt.figure(figsize=(12,6))
    plt.bar(sorted_results["tmID"], sorted_results["Win %"])
    plt.title("WNBA Team Playoff Series Win Percentage")
    plt.xlabel("Team")
    plt.ylabel("Win Percentage")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def max_wins():
    df = sd.teams_post_df.copy()
    max_wins_by_year = df.groupby('year')['W'].max().reset_index()
    max_wins_by_year.columns = ['year', 'Max_W']

    result_df = pd.merge(df, max_wins_by_year, 
                        left_on=['year', 'W'], 
                        right_on=['year', 'Max_W'], 
                        how='inner')

    final_df = result_df[['year', 'tmID', 'W']].drop_duplicates()
    final_df.columns = ['Year', 'Winning Team ID', 'Max Wins']
    return final_df