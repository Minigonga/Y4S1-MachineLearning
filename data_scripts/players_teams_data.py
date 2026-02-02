import pandas as pd
import numpy as np
from data_scripts import _store_data as sd
import plotly.express as px
import plotly.graph_objects as go


def offense_score_per_game(PTS, AST, FGM, FGA, TOV, GP):
    if GP == 0 or FGA == 0:
        return 0
    FG_percent = FGM / FGA
    return (PTS / GP) + 1.5 * (AST / GP) + 10 * FG_percent - 2 * (TOV / GP)


def defense_score_per_game(REB, STL, BLK, PF, GP):
    if GP == 0:
        return 0
    return 1.2 * (REB / GP) + 3 * (STL / GP) + 2 * (BLK / GP) - 1 * (PF / GP)


def overall_performance_per_game(PTS, REB, AST, STL, BLK, TOV, FGM, FGA, GP):
    if GP == 0 or FGA == 0:
        return 0 
    FG_percent = FGM / FGA
    return (
        (PTS / GP) +
        (REB / GP) * 1.2 +
        (AST / GP) * 1.5 +
        (STL / GP) * 3 +
        (BLK / GP) * 2 -
        (TOV / GP) * 2 +
        FG_percent * 10
    )


def average_players_perfomance():
    df = sd.players_teams_df.copy()
    df['Performance'] = df.apply(
        lambda row: overall_performance_per_game(
            row['points'], row['rebounds'], row['assists'], row['steals'],
            row['blocks'], row['turnovers'], row['fgMade'], row['fgAttempted'], row['GP']
        ), axis=1
    )
    avg_perf_per_player = df.groupby('playerID')['Performance'].mean().reset_index()
    
    # Histogram: Player Performance Distribution
    fig1 = px.histogram(avg_perf_per_player, x='Performance', nbins=15, marginal="box",
                        title='Distribution of Player Performance per Game', labels={'Performance':'Performance'})
    
    # Average Performance per Season
    avg_per_season = df.groupby('year')['Performance'].mean().reset_index()
    fig2 = px.bar(avg_per_season, x='year', y='Performance', 
                  title='Average Player Performance per Season', labels={'Performance':'Average Performance', 'year':'Season'})
    
    # Violin plot: Distribution per Player per Season
    avg_player_year = df.groupby(['playerID','year'])['Performance'].mean().reset_index()
    fig3 = px.violin(avg_player_year, x='year', y='Performance', box=True, points='all',
                     title='Distribution of Player Performance per Season', labels={'Performance':'Performance', 'year':'Season'})
    # Add background zones
    fig3.add_hrect(y0=avg_player_year['Performance'].min(), y1=10, fillcolor='#e74c3c', opacity=0.2, line_width=0)
    fig3.add_hrect(y0=10, y1=25, fillcolor='#f1c40f', opacity=0.2, line_width=0)
    fig3.add_hrect(y0=25, y1=40, fillcolor='#27ae60', opacity=0.2, line_width=0)
    fig3.add_hrect(y0=40, y1=avg_player_year['Performance'].max(), fillcolor='#006ab1', opacity=0.2, line_width=0)
    
    fig1.show()
    fig2.show()
    fig3.show()


def off_def_players_perfomance():
    df = sd.players_teams_df.copy()
    df['OffPerformance'] = df.apply(
        lambda row: offense_score_per_game(
            row['points'], row['assists'], row['fgMade'], row['fgAttempted'], row['turnovers'], row['GP']
        ), axis=1
    )
    df['DefPerformance'] = df.apply(
        lambda row: defense_score_per_game(
            row['rebounds'], row['steals'], row['blocks'], row['PF'], row['GP']
        ), axis=1
    )
    
    avg_off_player_year = df.groupby(['playerID','year'])['OffPerformance'].mean().reset_index()
    avg_def_player_year = df.groupby(['playerID','year'])['DefPerformance'].mean().reset_index()
    
    # Offensive Performance Violin Plot
    fig_off = px.violin(avg_off_player_year, x='year', y='OffPerformance', box=True, points='all',
                        title='Distribution of Offensive Performance per Season', labels={'OffPerformance':'Offensive Performance'})
    fig_off.add_hrect(y0=avg_off_player_year['OffPerformance'].min(), y1=5, fillcolor='#e74c3c', opacity=0.2, line_width=0)
    fig_off.add_hrect(y0=5, y1=17, fillcolor='#f1c40f', opacity=0.2, line_width=0)
    fig_off.add_hrect(y0=17, y1=25, fillcolor='#27ae60', opacity=0.2, line_width=0)
    fig_off.add_hrect(y0=25, y1=avg_off_player_year['OffPerformance'].max(), fillcolor='#006ab1', opacity=0.2, line_width=0)
    
    # Defensive Performance Violin Plot
    fig_def = px.violin(avg_def_player_year, x='year', y='DefPerformance', box=True, points='all',
                        title='Distribution of Defensive Performance per Season', labels={'DefPerformance':'Defensive Performance'})
    fig_def.add_hrect(y0=avg_def_player_year['DefPerformance'].min(), y1=2, fillcolor='#e74c3c', opacity=0.2, line_width=0)
    fig_def.add_hrect(y0=2, y1=10, fillcolor='#f1c40f', opacity=0.2, line_width=0)
    fig_def.add_hrect(y0=10, y1=14, fillcolor='#27ae60', opacity=0.2, line_width=0)
    fig_def.add_hrect(y0=14, y1=avg_def_player_year['DefPerformance'].max(), fillcolor='#006ab1', opacity=0.2, line_width=0)
    
    fig_off.show()
    fig_def.show()


def player_teammates_corr(min_seasons: int = 3, plot: bool = True, top_n: int = 10):
    df = sd.players_teams_df.copy()
    df['Performance'] = df.apply(
        lambda row: overall_performance_per_game(
            row['points'], row['rebounds'], row['assists'], row['steals'],
            row['blocks'], row['turnovers'], row['fgMade'], row['fgAttempted'], row['GP']
        ), axis=1
    )
    df = df.groupby(['playerID','year','tmID'], as_index=False)['Performance'].mean()
    team_avg = df.groupby(['tmID','year'], as_index=False).agg(team_avg_perf=('Performance','mean'),
                                                                team_size=('Performance','count'))
    df = df.merge(team_avg, on=['tmID','year'], how='left')
    df['teammates_avg_perf'] = (df['team_avg_perf'] * df['team_size'] - df['Performance']) / (df['team_size']-1)
    
    season_counts = df.groupby('playerID')['year'].nunique()
    valid_players = season_counts[season_counts >= min_seasons].index
    df = df[df['playerID'].isin(valid_players)]
    
    results = []
    for player, player_data in df.groupby('playerID'):
        if player_data['Performance'].nunique()<2 or player_data['teammates_avg_perf'].nunique()<2:
            continue
        corr = player_data['Performance'].corr(player_data['teammates_avg_perf'])
        results.append({'playerID':player, 'corr_with_teammates':corr})
    
    corr_df = pd.DataFrame(results)
    avg_corr = corr_df['corr_with_teammates'].mean()
    print(f"Average correlation with teammates (across seasons): {avg_corr:.4f}")
    
    if plot and not corr_df.empty:
        fig = px.histogram(corr_df, x='corr_with_teammates', nbins=20, title='Distribution of Player–Teammate Correlations',
                           labels={'corr_with_teammates':'Correlation'})
        fig.show()


def perf_per_min():
    df = sd.players_teams_df.copy()
    df['Performance'] = df.apply(
        lambda row: overall_performance_per_game(
            row['points'], row['rebounds'], row['assists'], row['steals'],
            row['blocks'], row['turnovers'], row['fgMade'], row['fgAttempted'], row['minutes']
        ), axis=1
    )
    avg_player_year = df.groupby(['playerID','year'])['Performance'].mean().reset_index()
    
    fig = px.strip(avg_player_year, x='year', y='Performance', stripmode='overlay', title='Player Performance per Season (Swarm Plot)',
                   labels={'Performance':'Performance', 'year':'Season'})
    
    fig.add_hrect(y0=avg_player_year['Performance'].min(), y1=3, fillcolor='#e74c3c', opacity=0.15, line_width=0)
    fig.add_hrect(y0=3, y1=5, fillcolor='#f1c40f', opacity=0.15, line_width=0)
    fig.add_hrect(y0=5, y1=7, fillcolor='#27ae60', opacity=0.15, line_width=0)
    fig.add_hrect(y0=7, y1=avg_player_year['Performance'].max(), fillcolor='#006ab1', opacity=0.15, line_width=0)
    
    fig.show()


def gs_gp():
    df = sd.players_teams_df.copy()
    avg_stats = df.groupby('year')[['GP','GS']].mean().reset_index()
    fig = go.Figure(data=[
        go.Bar(name='Games Played', x=avg_stats['year'], y=avg_stats['GP']),
        go.Bar(name='Games Started', x=avg_stats['year'], y=avg_stats['GS'])
    ])
    fig.update_layout(title='Average Games Played and Games Started per Year', barmode='group',
                      xaxis_title='Year', yaxis_title='Average Games')
    fig.show()


def avg_mins():
    df = sd.players_teams_df.copy()
    avg_mins = df.groupby('year', as_index=False)['minutes'].mean()
    fig = px.bar(avg_mins, x='year', y='minutes', title='Average Minutes Played per Year', labels={'minutes':'Average Minutes','year':'Year'})
    fig.show()
