from data_scripts import _store_data as sd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from IPython.display import display
pd.set_option('display.max_colwidth', None)

awards = pd.DataFrame()
coaches = pd.DataFrame()
players = pd.DataFrame()
merged_players = pd.DataFrame()

def load_dataset():
    global awards, coaches, players, merged_players

    awards = sd.awards_players_df.copy()
    players = sd.players_teams_df.copy()
    coaches = sd.coaches_df.copy()

    merged_players = pd.merge(awards, players, on=["playerID", "year"], how="inner")


metric_explanations = {
    "won": "Games won",
    "lost": "Games lost",
    "post_wins": "Playoff games won",
    "post_losses": "Playoff games lost",
    "MPG": "Minutes per game",
    "PPG": "Points per game",
    "RPG": "Rebounds per game",
    "APG": "Assists per game",
    "SPG": "Steals per game",
    "BPG": "Blocks per game",
    "DRPG": "Defensive rebounds per game",
    "TOV/G": "Turnovers per game",
    "PF/G": "Personal fouls per game",
    "DQ/G": "Disqualifications per game",
    "FG%": "Field goal percentage",
    "3P%": "Three-point percentage",
    "FT%": "Free throw percentage",
    "TS%": "True shooting percentage",
    "Win%": "Winning percentage",
    "PostWin%": "Postseason win percentage",
    "PPG_Improvement": "Increase in points per game from previous season",
    "RPG_Improvement": "Increase in rebounds per game from previous season",
    "APG_Improvement": "Increase in assists per game from previous season",
    "%GamesStarted": "Percentage of games started",
    "PostPPG": "Postseason points per game",
    "PostRPG": "Postseason rebounds per game",
    "PostAPG": "Postseason assists per game",
    "PostFG%": "Postseason field goal percentage"
}

def plot_award_correlation(df, award_col, title, metrics):
    df = df.copy()
    df[metrics + [award_col]] = df[metrics + [award_col]].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=metrics)

    correlations = df[metrics + [award_col]].corr()[award_col].drop(award_col).sort_values(ascending=False)
    
    # Colors for positive vs negative correlations
    colors = ['blue' if x > 0 else 'red' for x in correlations.values]

    # Plot using Plotly
    fig = go.Figure(go.Bar(
        x=correlations.values,
        y=correlations.index,
        orientation='h',
        marker_color=colors,
        text=[f"{v:.2f}" for v in correlations.values],
        textposition="outside"
    ))
    fig.update_layout(
        title=title,
        xaxis_title='Correlation with Winning Award',
        yaxis_title='Metrics',
        template='plotly_white',
        width=800,
        height=350
    )
    fig.show()

    print(f"\n📊 Correlation Analysis: {title}")
    print("=" * 80)
    for metric in correlations.index:
        corr_value = correlations[metric]
        print(f"  {metric:20s}: {corr_value:+.3f}  |  {metric_explanations.get(metric, 'No description')}")
    print("-" * 80)


def asgmvp_analyze():
    asg_years = merged_players[merged_players['award'] == "All-Star Game Most Valuable Player"]['year'].unique()
    data = players[players['year'].isin(asg_years)].copy()
    
    data["MPG"] = data["minutes"] / data["GP"]
    data["PPG"] = data["points"] / data["GP"]
    data["APG"] = data["assists"] / data["GP"]
    data["RPG"] = data["rebounds"] / data["GP"]
    data["FG%"] = data["fgMade"] / data["fgAttempted"].replace(0, pd.NA)
    data["3P%"] = data["threeMade"] / data["threeAttempted"].replace(0, pd.NA)
    data["FT%"] = data["ftMade"] / data["ftAttempted"].replace(0, pd.NA)
    data["TS%"] = data["points"] / (2 * (data["fgAttempted"] + 0.44 * data["ftAttempted"]).replace(0, pd.NA))
    
    asg_mvp_winners = merged_players[merged_players['award'] == "All-Star Game Most Valuable Player"][['playerID', 'year']]
    data = pd.merge(data, asg_mvp_winners, on=['playerID', 'year'], how='left', indicator=True)
    data['won_award'] = (data['_merge'] == 'both').astype(int)
    data = data.drop('_merge', axis=1)

    metrics = ["MPG", "PPG", "APG", "RPG", "FG%", "3P%", "FT%", "TS%"]
    plot_award_correlation(data, 'won_award', "All-Star Game MVP — Correlation with Winning Award", metrics)


def coy_analyze():
    coy_years = awards[awards["award"] == "Coach of the Year"]['year'].unique()
    data = coaches[coaches['year'].isin(coy_years)].copy()
    
    data["Games"] = data["won"] + data["lost"]
    data["Win%"] = data["won"] / data["Games"].replace(0, pd.NA)
    data["PostWin%"] = data["post_wins"] / (data["post_wins"] + data["post_losses"]).replace(0, pd.NA)
    
    coy_winners = awards[awards["award"] == "Coach of the Year"].rename(columns={"playerID": "coachID"})[['coachID', 'year']]
    data = pd.merge(data, coy_winners, on=['coachID', 'year'], how='left', indicator=True)
    data['won_award'] = (data['_merge'] == 'both').astype(int)
    data = data.drop('_merge', axis=1)

    metrics = ["won", "lost", "Win%", "post_wins", "post_losses", "PostWin%"]
    plot_award_correlation(data, 'won_award', "Coach of the Year — Correlation with Winning Award", metrics)


def dpoy_analyze():
    dpoy_years = merged_players[merged_players["award"] == "Defensive Player of the Year"]['year'].unique()
    data = players[players['year'].isin(dpoy_years)].copy()
    
    data["SPG"] = data["steals"] / data["GP"]
    data["BPG"] = data["blocks"] / data["GP"]
    data["DRPG"] = data["dRebounds"] / data["GP"]
    data["TOV/G"] = data["turnovers"] / data["GP"]
    
    dpoy_winners = merged_players[merged_players["award"] == "Defensive Player of the Year"][['playerID', 'year']]
    data = pd.merge(data, dpoy_winners, on=['playerID', 'year'], how='left', indicator=True)
    data['won_award'] = (data['_merge'] == 'both').astype(int)
    data = data.drop('_merge', axis=1)

    metrics = ["SPG", "BPG", "DRPG", "TOV/G"]
    plot_award_correlation(data, 'won_award', "Defensive Player of the Year — Correlation with Winning Award", metrics)


def kpsw_analyze():
    kpsw_years = merged_players[merged_players["award"] == "Kim Perrot Sportsmanship Award"]['year'].unique()
    data = players[players['year'].isin(kpsw_years)].copy()
    
    data["PF/G"] = data["PF"] / data["GP"]
    data["DQ/G"] = data["dq"] / data["GP"]
    
    kpsw_winners = merged_players[merged_players["award"] == "Kim Perrot Sportsmanship Award"][['playerID', 'year']]
    data = pd.merge(data, kpsw_winners, on=['playerID', 'year'], how='left', indicator=True)
    data['won_award'] = (data['_merge'] == 'both').astype(int)
    data = data.drop('_merge', axis=1)

    metrics = ["PF/G", "DQ/G"]
    plot_award_correlation(data, 'won_award', "Kim Perrot Sportsmanship Award — Correlation with Winning Award", metrics)


def mip_analyze():
    mip_years = merged_players[merged_players["award"] == "Most Improved Player"]['year'].unique()
    data = players[players['year'].isin(mip_years)].copy()
    
    prev_year = players.copy()
    prev_year["year"] -= 1
    combined = pd.merge(data, prev_year, on="playerID", suffixes=("", "_prev"))

    combined["PPG_Improvement"] = (combined["points"] / combined["GP"]) - (combined["points_prev"] / combined["GP_prev"])
    combined["RPG_Improvement"] = (combined["rebounds"] / combined["GP"]) - (combined["rebounds_prev"] / combined["GP_prev"])
    combined["APG_Improvement"] = (combined["assists"] / combined["GP"]) - (combined["assists_prev"] / combined["GP_prev"])
    
    mip_winners = merged_players[merged_players["award"] == "Most Improved Player"][['playerID', 'year']]
    combined = pd.merge(combined, mip_winners, on=['playerID', 'year'], how='left', indicator=True)
    combined['won_award'] = (combined['_merge'] == 'both').astype(int)
    combined = combined.drop('_merge', axis=1)

    metrics = ["PPG_Improvement", "RPG_Improvement", "APG_Improvement"]
    plot_award_correlation(combined, 'won_award', "Most Improved Player — Correlation with Winning Award", metrics)


def mvp_analyze():
    mvp_years = merged_players[merged_players["award"] == "Most Valuable Player"]['year'].unique()
    data = players[players['year'].isin(mvp_years)].copy()
    
    data["PPG"] = data["points"] / data["GP"]
    data["RPG"] = data["rebounds"] / data["GP"]
    data["APG"] = data["assists"] / data["GP"]
    data["TS%"] = data["points"] / (2 * (data["fgAttempted"] + 0.44 * data["ftAttempted"]).replace(0, pd.NA))
    
    mvp_winners = merged_players[merged_players["award"] == "Most Valuable Player"][['playerID', 'year']]
    data = pd.merge(data, mvp_winners, on=['playerID', 'year'], how='left', indicator=True)
    data['won_award'] = (data['_merge'] == 'both').astype(int)
    data = data.drop('_merge', axis=1)

    metrics = ["PPG", "RPG", "APG", "TS%"]
    plot_award_correlation(data, 'won_award', "Most Valuable Player — Correlation with Winning Award", metrics)


def roty_analyze():
    roty_years = merged_players[merged_players["award"] == "Rookie of the Year"]['year'].unique()
    data = players[players['year'].isin(roty_years)].copy()
    
    prev_players = players[['playerID', 'year']]
    data['is_rookie'] = ~data.apply(lambda row: ((prev_players['playerID'] == row['playerID']) & 
                                                (prev_players['year'] == row['year'] - 1)).any(), axis=1)
    
    data = data[data['is_rookie']]
    
    data["PPG"] = data["points"] / data["GP"]
    data["RPG"] = data["rebounds"] / data["GP"]
    data["APG"] = data["assists"] / data["GP"]
    data["SPG"] = data["steals"] / data["GP"]
    data["BPG"] = data["blocks"] / data["GP"]
    
    roty_winners = merged_players[merged_players["award"] == "Rookie of the Year"][['playerID', 'year']]
    data = pd.merge(data, roty_winners, on=['playerID', 'year'], how='left', indicator=True)
    data['won_award'] = (data['_merge'] == 'both').astype(int)
    data = data.drop(['_merge', 'is_rookie'], axis=1)

    metrics = ["PPG", "RPG", "APG", "SPG", "BPG"]
    plot_award_correlation(data, 'won_award', "Rookie of the Year — Correlation with Winning Award", metrics)

def roty_rank_of_team():
    roty_years = merged_players[merged_players["award"] == "Rookie of the Year"]['year'].unique()
    data = players[players['year'].isin(roty_years)].copy()
    
    prev_players = players[['playerID', 'year']]
    data['is_rookie'] = ~data.apply(lambda row: ((prev_players['playerID'] == row['playerID']) & 
                                                 (prev_players['year'] == row['year'] - 1)).any(), axis=1)
    data = data[data['is_rookie']]
    
    roty_winners = merged_players[merged_players["award"] == "Rookie of the Year"][['playerID', 'year']]
    data = pd.merge(data, roty_winners, on=['playerID', 'year'], how='left', indicator=True)
    data['won_award'] = (data['_merge'] == 'both').astype(int)
    data = data.drop(['_merge', 'is_rookie'], axis=1)
    
    prev_year_teams = sd.teams_df[['tmID', 'year', 'rank']].copy()
    prev_year_teams['year'] += 1
    
    data = data[data['won_award'] == 1]
    data = data[data['year'] != 1]  
    
    data = pd.merge(data, prev_year_teams, left_on=['tmID', 'year'], right_on=['tmID', 'year'], how='left')
    data = data.rename(columns={'rank': 'prev_year_team_rank'})
    
    display(data[['playerID', 'year', 'tmID', 'prev_year_team_rank']].sort_values(by=['year', 'prev_year_team_rank']))

def smoy_analyze():
    smoy_years = merged_players[merged_players["award"] == "Sixth Woman of the Year"]['year'].unique()
    data = players[players['year'].isin(smoy_years)].copy()
    
    data["PPG"] = data["points"] / data["GP"]
    data["RPG"] = data["rebounds"] / data["GP"]
    data["APG"] = data["assists"] / data["GP"]
    data["%GamesStarted"] = data["GS"] / data["GP"]
    
    smoy_winners = merged_players[merged_players["award"] == "Sixth Woman of the Year"][['playerID', 'year']]
    data = pd.merge(data, smoy_winners, on=['playerID', 'year'], how='left', indicator=True)
    data['won_award'] = (data['_merge'] == 'both').astype(int)
    data = data.drop('_merge', axis=1)

    metrics = ["PPG", "RPG", "APG", "%GamesStarted"]
    plot_award_correlation(data, 'won_award', "Sixth Woman of the Year — Correlation with Winning Award", metrics)


def fmvp_analyze():
    fmvp_years = merged_players[merged_players["award"] == "WNBA Finals Most Valuable Player"]['year'].unique()
    data = players[players['year'].isin(fmvp_years)].copy()
    
    data["PostPPG"] = data["PostPoints"] / data["PostGP"].replace(0, pd.NA)
    data["PostRPG"] = data["PostRebounds"] / data["PostGP"].replace(0, pd.NA)
    data["PostAPG"] = data["PostAssists"] / data["PostGP"].replace(0, pd.NA)
    data["PostFG%"] = data["PostfgMade"] / data["PostfgAttempted"].replace(0, pd.NA)
    
    fmvp_winners = merged_players[merged_players["award"] == "WNBA Finals Most Valuable Player"][['playerID', 'year']]
    data = pd.merge(data, fmvp_winners, on=['playerID', 'year'], how='left', indicator=True)
    data['won_award'] = (data['_merge'] == 'both').astype(int)
    data = data.drop('_merge', axis=1)

    metrics = ["PostPPG", "PostRPG", "PostAPG", "PostFG%"]
    plot_award_correlation(data, 'won_award', "Finals MVP — Correlation with Winning Award", metrics)

def analyse_all_decade_team_positions():
    players = sd.awards_players_df[
        sd.awards_players_df["award"] == "WNBA All-Decade Team"
    ][["playerID"]]
    data = sd.players_df.merge(
        players,
        left_on=["bioID"],
        right_on=["playerID"],
        how="inner"
    )
    print("All-Decade Team Members:")
    display(data[["playerID", "pos"]])
    players = sd.awards_players_df[
    sd.awards_players_df["award"] == "WNBA All Decade Team Honorable Mention"
    ][["playerID"]]
    data = sd.players_df.merge(
        players,
        left_on=["bioID"],
        right_on=["playerID"],
        how="inner"
    )
    print("\nHonorable Players:")
    display(data[["playerID", "pos"]])

def players_multiple_awards_filtered():
    filtered_awards = merged_players[
        ~merged_players['award'].isin(['WNBA All-Decade Team', 'WNBA All Decade Team Honorable Mention'])
    ].copy()
    
    grouped = filtered_awards.groupby(['playerID', 'year'])['award'].apply(list).reset_index()
    
    grouped['num_awards'] = grouped['award'].apply(len)
    
    grouped['multiple_awards'] = grouped['num_awards'] > 1
    
    result = grouped[grouped['multiple_awards']]

    result = result.sort_values(by=['year', 'playerID']).reset_index(drop=True)

    display(result)