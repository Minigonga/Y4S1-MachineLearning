import pandas as pd
from pathlib import Path

def load_player_test_data(data_dir, year):
    base_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parent.parent / "basketballPlayoffs"
    players_teams_df = pd.read_csv(base_dir / "players_teams.csv")
    playerTeamsTest_df = players_teams_df.loc[players_teams_df['year'] == year, ['playerID', 'year', 'tmID', 'lgID', 'stint']]
    playerTeamsTest_df = playerTeamsTest_df[playerTeamsTest_df['stint'].isin([0, 1])]
    playerTeamsTest_df['stint'] = playerTeamsTest_df['stint'].replace(1, 0)
    return playerTeamsTest_df

def load_coach_test_data(data_dir, year):
    base_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parent.parent / "basketballPlayoffs"
    coaches_df = pd.read_csv(base_dir / "coaches.csv")
    coachesTest_df = coaches_df.loc[coaches_df['year'] == year, ['coachID', 'year', 'tmID', 'lgID', 'stint']]
    coachesTest_df = coachesTest_df[coachesTest_df['stint'].isin([0, 1])]
    coachesTest_df['stint'] = coachesTest_df['stint'].replace(1, 0)
    return coachesTest_df

def load_teams_test_data(data_dir, year):
    base_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parent.parent / "basketballPlayoffs"
    teams_df = pd.read_csv(base_dir / "teams.csv")
    teamsTest_df = teams_df.loc[teams_df['year'] == year, ['tmID', 'franchID', 'year', 'confID', 'lgID', 'name', 'arena']]
    return teamsTest_df

def load_rookies_test_data(data_dir, year):
    base_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parent.parent / "basketballPlayoffs"
    players_teams_df = pd.read_csv(base_dir / "players_teams.csv")
    playerTeamsTest_df = players_teams_df[['playerID', 'year', 'tmID', 'lgID', 'stint']].copy()
    playerTeamsTest_df = playerTeamsTest_df[playerTeamsTest_df['stint'].isin([0, 1])]
    playerTeamsTest_df['stint'] = playerTeamsTest_df['stint'].replace(1, 0)
    min_year_df = playerTeamsTest_df.groupby('playerID')['year'].min().reset_index()
    rookiesTeamTest_df = min_year_df[min_year_df['year'] == year]
    rookiesTeamTest_df = rookiesTeamTest_df.merge(
        playerTeamsTest_df,
        on=['playerID', 'year'],
        how='left'
    )

    return rookiesTeamTest_df