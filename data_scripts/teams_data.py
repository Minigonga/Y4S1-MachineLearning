import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from data_scripts import _store_data as sd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def fix_missing_values():
    round_order = ['firstRound', 'semis', 'finals']
    round_map = {'FR': 'firstRound', 'CF': 'semis', 'F': 'finals'}

    for this_year in sd.series_post_df['year'].unique():
        year_results = sd.series_post_df[sd.series_post_df['year'] == this_year]

        for tm in sd.teams_df.loc[sd.teams_df['year'] == this_year, 'tmID']:
            team_row = sd.teams_df[
                (sd.teams_df['year'] == this_year) & (sd.teams_df['tmID'] == tm)
            ]

            for i, r in enumerate(round_order[:-1]):
                next_r = round_order[i + 1]

                if team_row[r].iloc[0] == "W" and (pd.isna(team_row[next_r].iloc[0]) or team_row[next_r].iloc[0] == ""):
                    next_round_results = year_results[year_results['round'] == list(round_map.keys())[i + 1]]

                    if tm in next_round_results['tmIDWinner'].values:
                        result = "W"
                    elif tm in next_round_results['tmIDLoser'].values:
                        result = "L"
                    else:
                        continue

                    sd.teams_df.loc[
                        (sd.teams_df['year'] == this_year) & (sd.teams_df['tmID'] == tm),
                        next_r
                    ] = result

def teams_series_appearances():
    series_counts = (
        sd.teams_df.assign(
            SeriesPlayed = sd.teams_df[["firstRound", "semis", "finals"]]
                        .apply(lambda x: sum(val in ["W", "L"] for val in x), axis=1)
        )
        .groupby("tmID")["SeriesPlayed"]
        .sum()
        .reset_index()
    )

    series_counts = series_counts.sort_values(by="SeriesPlayed", ascending=False)

    plt.figure(figsize=(12,6))
    plt.bar(series_counts["tmID"], series_counts["SeriesPlayed"])
    plt.title("WNBA Team Total Playoff Series Appearances")
    plt.xlabel("Team")
    plt.ylabel("Total Series Played")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def teams_regular_season_wins_trend():
    wins_per_team = sd.teams_df.groupby(['year', 'name'])['won'].sum().reset_index()
    
    fig = px.line(
        wins_per_team, 
        x='year', 
        y='won', 
        color='name', 
        markers=True,
        title="Number of Wins per Year for Each Team (Regular Season)",
        labels={'year':'Year', 'won':'Regular Season Wins', 'name':'Team'}
    )
    
    fig.update_layout(
        legend_title_text='Team',
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        ),
        xaxis=dict(dtick=1),
        yaxis=dict(rangemode='tozero')
    )
    
    fig.show()

def teams_regular_season_rank_trend():
    # Aggregate rank by year and team
    rank_per_team = sd.teams_df.groupby(["year", "confID", "name"])["rank"].mean().reset_index()

    # Create subplot: 1 row, 2 columns (East & West)
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Eastern Conference", "Western Conference"),
        shared_yaxes=True
    )

    # East
    east_df = rank_per_team[rank_per_team["confID"] == "EA"]
    for team in east_df["name"].unique():
        team_data = east_df[east_df["name"] == team]
        fig.add_trace(
            go.Scatter(
                x=team_data["year"],
                y=team_data["rank"],
                mode="lines+markers",
                name=team,
                showlegend=True
            ),
            row=1, col=1
        )

    # West
    west_df = rank_per_team[rank_per_team["confID"] == "WE"]
    for team in west_df["name"].unique():
        team_data = west_df[west_df["name"] == team]
        fig.add_trace(
            go.Scatter(
                x=team_data["year"],
                y=team_data["rank"],
                mode="lines+markers",
                name=team,
                showlegend=False  # legend only on left side
            ),
            row=1, col=2
        )

    # Formatting
    fig.update_layout(
        title="Team Conference Rank Trends Over Time",
        xaxis_title="Year",
        yaxis_title="Rank (Lower is Better)",
        xaxis=dict(dtick=1),
        yaxis=dict(autorange="reversed"),  # rank 1 at top
        legend_title="Teams"
    )

    fig.show()

def efficiency_scatter():
    df = sd.teams_df.copy()

    df['possessions'] = df['o_fga'] + 0.44 * df['o_fta'] - df['o_oreb'] + df['o_to']
    df['off_eff'] = df['o_pts'] / df['possessions']
    df['def_eff'] = df['d_pts'] / df['possessions']
    df['off_eff_scaled'] = (df['off_eff'] - df['off_eff'].min()) / (df['off_eff'].max() - df['off_eff'].min()) * 100
    df['def_eff_scaled'] = (df['def_eff'] - df['def_eff'].min()) / (df['def_eff'].max() - df['def_eff'].min()) * 100

    fig = px.scatter(
        df,
        x='off_eff_scaled',
        y='def_eff_scaled',
        color=df['playoff'].map({'Y': 'Made Playoffs', 'N': 'Did Not Make Playoffs'}),
        hover_data=['tmID', 'year', 'name'],
        title='🏀 Scaled Offensive vs Defensive Efficiency with Playoff Participation',
        labels={
            'off_eff_scaled': 'Offensive Efficiency (Higher -> Better)',
            'def_eff_scaled': 'Defensive Efficiency (Lower -> Better)',
            'color': 'Playoff Status'
        }
    )

    # Invert y-axis so better defense is higher
    fig.update_yaxes(autorange='reversed')

    fig.update_traces(marker=dict(size=8, opacity=0.8))
    fig.show()






def prepare_team_stats():
    df = sd.teams_df.copy()

    df['PTS_pg'] = df['o_pts'] / df['GP']
    df['REB_pg'] = df['o_reb'] / df['GP']
    df['AST_pg'] = df['o_asts'] / df['GP']
    df['STL_pg'] = df['o_stl'] / df['GP']
    df['BLK_pg'] = df['o_blk'] / df['GP']
    df['TO_pg']  = df['o_to'] / df['GP']
    df['PF_pg']  = df['o_pf'] / df['GP']

    df['OPP_PTS_pg'] = df['d_pts'] / df['GP']
    df['OPP_REB_pg'] = df['d_reb'] / df['GP']
    df['FORCED_TO_pg'] = df['d_to'] / df['GP']

    df['stat_score'] = (
        (df['PTS_pg'] + df['REB_pg'] + df['AST_pg']) * 1.0 +
        (df['STL_pg'] + df['BLK_pg'] + df['FORCED_TO_pg']) * 1.2 -
        (df['TO_pg'] + df['PF_pg']) * 1.0 -
        (df['OPP_PTS_pg'] * 0.8 + df['OPP_REB_pg'] * 0.5)
    )
    df['stat_score'] = (df['stat_score'] - df['stat_score'].min()) / (df['stat_score'].max() - df['stat_score'].min()) * 100

    df['win_percentage'] = (df['won'] / (df['won'] + df['lost'])) * 100
    df['win_percentage'] = df['win_percentage'].fillna(0)

    df['overall_performance'] = (df['stat_score'] + df['win_percentage']) / 2
    df['rank_score'] = df['rank'].max() - df['rank'] + 1

    return df


def correlation_heatmap():
    df = prepare_team_stats()
    corr_df = df[['attend', 'stat_score', 'win_percentage', 'overall_performance', 'rank_score']].copy()
    correlation_matrix = corr_df.corr(numeric_only=True)

    heatmap = go.Figure(
        data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='RdBu',
            zmin=-1,
            zmax=1,
            text=correlation_matrix.round(2).values,
            texttemplate='%{text}',
            textfont={"size": 12},
            hoverongaps=False
        )
    )
    heatmap.update_layout(
        title="🔗 Correlation Heatmap: Attendance, Performance, Rank",
        width=700,
        height=600,
        xaxis_title="Metrics",
        yaxis_title="Metrics"
    )
    heatmap.show()


def attendance_vs_performance():
    df = prepare_team_stats()

    melted = df.melt(
        id_vars=['attend', 'rank_score', 'tmID', 'year', 'arena'],
        value_vars=['stat_score', 'win_percentage', 'overall_performance'],
        var_name='Metric',
        value_name='Value'
    )

    fig = px.scatter(
        melted,
        x='Value',
        y='attend',
        color='Metric',
        symbol='Metric',
        hover_data=['tmID', 'year', 'arena', 'rank_score'],
        title='📈 Attendance vs Team Performance Metrics (Stats, Wins, Overall)',
        labels={'Value': 'Performance Metric (Scaled)', 'attend': 'Attendance'}
    )
    fig.update_traces(marker=dict(size=6, opacity=0.8))
    fig.show()



def playoff_comparison():
    df = sd.teams_df.copy()
    stats = df.groupby('playoff')[['won', 'lost']].mean().round(2)

    fig = go.Figure()
    for col in ['won', 'lost']:
        fig.add_trace(go.Bar(
            x=stats.index.astype(str),
            y=stats[col],
            name=col
        ))
    fig.update_layout(
        title='Playoff vs Non-Playoff Team Performance',
        barmode='group',
        xaxis_title='Playoff Status',
        yaxis_title='Average Value'
    )
    fig.show()


def regular_season_ranks():
    sd.teams_df['conf_rank'] = sd.teams_df.groupby(['year', 'confID'])['won'] \
                    .rank(method='dense', ascending=False) \
                    .astype(int)
    ranked_df = sd.teams_df.sort_values(by=['year', 'confID', 'conf_rank'])

    for (year, conf), group in ranked_df.groupby(['year', 'confID']):
        print(f"\n🏀 Year {year} | Conference {conf}")
        print(group[['tmID', 'name', 'confID', 'won', 'lost', 'conf_rank']].to_string(index=False))

    sd.teams_df.drop(columns=['conf_rank'], inplace=True)
    