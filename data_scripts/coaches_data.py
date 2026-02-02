from data_scripts import _store_data as sd
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt

def summarize_by_coach(df: pd.DataFrame) -> pd.DataFrame:
    coach_summary = df.groupby('coachID').agg(
        total_wins=('won', 'sum'),
        total_losses=('lost', 'sum'),
        total_post_wins=('post_wins', 'sum'),
        total_post_losses=('post_losses', 'sum'),
        seasons=('year', 'count')
    )
    coach_summary['career_win_pct'] = coach_summary['total_wins'] / (
        coach_summary['total_wins'] + coach_summary['total_losses']
    )
    return coach_summary.sort_values('total_wins', ascending=False).head(10)


def turnovers_by_coach():
    df = sd.coaches_df.copy()
    turnovers_by_coach = (
        df[df['stint'] == 1]                 
        .groupby('coachID', as_index=False)
        .agg(total_turnovers=('stint', 'count'))
        .sort_values('total_turnovers', ascending=False)
        .head(10)
    )
    return turnovers_by_coach


def plot_wins_losses_and_trend():
    df = sd.coaches_df.copy()
    df['win_pct'] = df['won'] / (df['won'] + df['lost'])
    
    # Scatter plot: Wins vs Losses
    fig1 = px.scatter(df, x='won', y='lost', title="Wins vs Losses by Season",
                      labels={'won': 'Wins', 'lost': 'Losses'}, opacity=0.7)
    
    # Line plot: Average wins per season
    avg_wins = df.groupby('year')['won'].mean().reset_index()
    fig2 = px.line(avg_wins, x='year', y='won', title="Average Wins per Season (League-wide)",
                   labels={'won': 'Average Wins', 'year': 'Year'})
    
    # Histogram: Distribution of win percentage
    fig3 = px.histogram(df, x='win_pct', nbins=15, marginal="box", title='Distribution of Win Percentage',
                        labels={'win_pct': 'Win Percentage'}, opacity=0.7)
    
    # Show plots sequentially
    fig1.show()
    fig2.show()
    fig3.show()


def analyze_wnba_coaches():
    df = sd.coaches_df.copy()
    df['win_pct'] = df['won'] / (df['won'] + df['lost'])
    df['loss_pct'] = df['lost'] / (df['won'] + df['lost'])
    df['turnover'] = np.where(df['stint'] == 1, 1, 0)
    
    # Correlation heatmap
    corr_matrix = df[['win_pct','loss_pct','turnover']].corr().round(2)
    heatmap = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        text=corr_matrix.values,
        texttemplate="%{text}"
    ))
    heatmap.update_layout(title='Correlation Heatmap')
    
    boxplot = px.box(df, x='turnover', y='win_pct', color='turnover',
                     title='Win Percentage vs Turnover', labels={'win_pct':'Win Percentage','turnover':'Turnover'})
    
    turnover_counts = df['turnover'].value_counts().reset_index()
    turnover_counts.columns = ['turnover','count']
    barplot = px.bar(turnover_counts, x='turnover', y='count', color='turnover',
                     title='Turnover Counts', labels={'turnover':'Turnover','count':'Count'},
                     color_discrete_map={0:'skyblue',1:'salmon'})
    
    # Show plots
    heatmap.show()
    boxplot.show()
    barplot.show()

def coach_tenure():
    df = sd.coaches_df.sort_values(["coachID", "tmID", "year"])
    df["tenure_year"] = df["year"] - df.groupby(["coachID", "tmID"])["year"].transform("min") + 1
    turnovers = df[df["stint"] == 1]
    plt.figure(figsize=(6,4))
    plt.hist(turnovers["tenure_year"])
    plt.xlabel("Tenure Year Coach Was Fired (with that team)")
    plt.ylabel("Number of Coaches")
    plt.title("Coach Turnover by Team Tenure Year")
    plt.tight_layout()
    plt.show()


def get_turnover_years():
    """
    Returns and displays a table of coach turnovers by year.
    Shows which years had coaching changes and which teams were affected.
    """
    df = sd.coaches_df.copy()
    
    turnovers = df[df['stint'] == 1].copy()
    
    yearly_summary = (
        turnovers.groupby('year')
        .agg(
            num_turnovers=('coachID', 'count'),
            teams=('tmID', lambda x: ', '.join(sorted(x.unique())))
        )
        .reset_index()
        .sort_values('year')
    )
    
    total_teams_per_year = df.groupby('year')['tmID'].nunique()
    yearly_summary['turnover_rate'] = (
        yearly_summary['num_turnovers'] / 
        yearly_summary['year'].map(total_teams_per_year)
    ).round(3)
    
    # Rename columns for better display
    yearly_summary.columns = ['Year', 'Num Turnovers', 'Teams Affected', 'Turnover Rate']
    
    # Display as formatted table
    print("\n=== COACH TURNOVERS BY YEAR ===\n")
    from IPython.display import display
    display(yearly_summary.style.format({
        'Turnover Rate': '{:.1%}'
    }).set_properties(**{
        'text-align': 'left'
    }))
    
    return yearly_summary