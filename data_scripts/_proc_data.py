from data_scripts import _store_data as ds

def cleanLgId():
    ds.awards_players_df = ds.awards_players_df.drop(columns=["lgID"])
    ds.coaches_df = ds.coaches_df.drop(columns=["lgID"])
    ds.players_teams_df = ds.players_teams_df.drop(columns=["lgID"])
    ds.series_post_df = ds.series_post_df.drop(columns=["lgIDWinner", "lgIDLoser"])
    ds.teams_post_df = ds.teams_post_df.drop(columns=["lgID"])
    ds.teams_df = ds.teams_df.drop(columns=["lgID"])

def cleanPlayers():
    bio_missing_birth = ds.players_df[ds.players_df["birthDate"] == "0000-00-00"]
    merged = ds.players_teams_df.merge(
        bio_missing_birth,
        left_on="playerID",
        right_on="bioID",
        how="inner"
    )
    merged2 = ds.awards_players_df.merge(
        bio_missing_birth,
        left_on="playerID",
        right_on="bioID",
        how="inner"
    )

    count = bio_missing_birth["bioID"].nunique()
    print("There are " + str(count)+ " players in the dataset players.csv without birthdate")
    count = merged["playerID"].nunique()
    print("There are " + str(count)+ " players of the dataset players.csv without birthdate that are in the players_teams.csv")
    count = merged2["playerID"].nunique()
    print("There are " + str(count)+ " players of the dataset players.csv without birthdate that are in the awarded_players.csv")

    def print_merged2():
        print(merged2)
    
    def print_merged3():
        merged3 = ds.coaches_df.merge(
            bio_missing_birth,
            left_on="coachID",
            right_on="bioID",
            how="inner"
        )

        count = bio_missing_birth["bioID"].nunique()
        print("There are " + str(count)+ " players in the dataset players.csv without birthdate")
        count = merged3["coachID"].nunique()
        print("There are " + str(count)+ " players of the dataset players.csv without birthdate that are in the coaches.csv")

    return print_merged2, print_merged3