import pandas as pd
from pathlib import Path

awards_players_df = pd.DataFrame()
coaches_df = pd.DataFrame()
players_teams_df = pd.DataFrame()
players_df = pd.DataFrame()
series_post_df = pd.DataFrame()
teams_post_df = pd.DataFrame()
teams_df = pd.DataFrame()

def read_and_store_data(data_dir: str = None):
    global awards_players_df, coaches_df, players_teams_df, players_df, series_post_df, teams_post_df, teams_df
    
    base_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parent.parent / "basketballPlayoffs"

    awards_players_df = pd.read_csv(base_dir / "awards_players.csv")
    coaches_df = pd.read_csv(base_dir / "coaches.csv")
    players_teams_df = pd.read_csv(base_dir / "players_teams.csv")
    players_df = pd.read_csv(base_dir / "players.csv")
    series_post_df = pd.read_csv(base_dir / "series_post.csv")
    teams_post_df = pd.read_csv(base_dir / "teams_post.csv")
    teams_df = pd.read_csv(base_dir / "teams.csv")

def df_info_table(df: pd.DataFrame) -> pd.DataFrame:
    info_df = pd.DataFrame({
        "Non-Null Count": df.notna().sum(),
        "Null Count": df.isna().sum(),
        "Missing %": (df.isna().sum() / len(df) * 100).round(2),
        "Dtype": df.dtypes.astype(str),
        "Unique Values": df.nunique(),
    })
    return info_df

def save_data(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    awards_players_df.to_pickle(output_dir / "awards_players.pkl")
    coaches_df.to_pickle(output_dir / "coaches.pkl")
    players_teams_df.to_pickle(output_dir / "players_teams.pkl")
    players_df.to_pickle(output_dir / "players.pkl")
    series_post_df.to_pickle(output_dir / "series_post.pkl")
    teams_post_df.to_pickle(output_dir / "teams_post.pkl")
    teams_df.to_pickle(output_dir / "teams.pkl")


def load_data(input_dir: Path):
    global awards_players_df, coaches_df, players_teams_df, players_df, series_post_df, teams_post_df, teams_df

    awards_players_path = input_dir / "awards_players.pkl"
    coaches_path = input_dir / "coaches.pkl"
    players_teams_path = input_dir / "players_teams.pkl"
    players_path = input_dir / "players.pkl"
    series_post_path = input_dir / "series_post.pkl"
    teams_post_path = input_dir / "teams_post.pkl"
    teams_path = input_dir / "teams.pkl"

    awards_players_df = pd.read_pickle(awards_players_path)
    coaches_df = pd.read_pickle(coaches_path)
    players_teams_df = pd.read_pickle(players_teams_path)
    players_df = pd.read_pickle(players_path)
    series_post_df = pd.read_pickle(series_post_path)
    teams_post_df = pd.read_pickle(teams_post_path)
    teams_df = pd.read_pickle(teams_path)