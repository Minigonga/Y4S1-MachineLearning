import pandas as pd     
import numpy as np        
import matplotlib.pyplot as plt
from data_scripts import _store_data as sd

def series_post_bracket_table():
    df_copy = sd.series_post_df.copy()

    def matchup_string(row):
        teams = [row['tmIDWinner'], row['tmIDLoser']]
        results = [row['W'], row['L']]
        if np.random.rand() > 0.5:
            teams = teams[::-1]
            results = results[::-1]

        if teams[0] == row['tmIDWinner']:
            teams[0] = r"$\bf{" + teams[0] + "}$"
            results[0] = r"$\bf{" + str(results[0]) + "}$"
        else:
            teams[1] = r"$\bf{" + teams[1] + "}$"
            results[1] = r"$\bf{" + str(results[1]) + "}$"

        return f"{teams[0]} vs {teams[1]}\n({results[0]}-{results[1]})"

    df_temp = df_copy.copy()
    df_temp["matchup"] = df_temp.apply(matchup_string, axis=1)

    df_temp["round_number"] = df_temp.groupby(["year","round"]).cumcount() + 1
    df_temp["col"] = df_temp["round"].str.upper() + df_temp["round_number"].astype(str)
    df_temp.loc[df_temp["round"]=="F", "col"] = "Final"

    bracket_temp = df_temp.pivot(index="year", columns="col", values="matchup").reset_index()
    cols_order = ["year","FR1","FR2","FR3","FR4","CF1","CF2","Final"]
    bracket_temp = bracket_temp[cols_order]
    bracket_temp = bracket_temp.rename(columns={"year": "Year"})

    # --- Plot the table ---
    fig, ax = plt.subplots(figsize=(14, len(bracket_temp)*0.75 + 1))
    ax.axis('off')

    tbl = ax.table(cellText=bracket_temp.values,
                colLabels=bracket_temp.columns,
                loc='center',
                cellLoc='center',
                colLoc='center')

    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 3)

    # --- Colors ---
    n_rows, n_cols = bracket_temp.shape

    for j in range(n_cols):
        tbl[0, j].set_facecolor('#40466e')
        tbl[0, j].set_text_props(color='w', weight='bold')

    for i in range(1, n_rows+1):
        for j in range(n_cols):
            if i % 2 == 0:
                tbl[i, j].set_facecolor('#f0f0f0')
            else:
                tbl[i, j].set_facecolor('white')

    # --- Title ---
    plt.title("WNBA Playoff Bracket Table", fontsize=14, pad=20)
    plt.show()



def series_wins_losses_count():
    df = sd.series_post_df
    
    win_df = df[['round', 'tmIDWinner', 'W']].rename(columns={'tmIDWinner': 'team', 'W': 'Wins'})
    lose_df = df[['round', 'tmIDLoser', 'L']].rename(columns={'tmIDLoser': 'team', 'L': 'Losses'})
    
    merged = pd.merge(win_df.groupby(['round', 'team'])['Wins'].sum(),
                      lose_df.groupby(['round', 'team'])['Losses'].sum(),
                      left_index=True, right_index=True, how='outer').fillna(0).reset_index()
    
    merged['Wins'] = merged['Wins'].astype(int)
    merged['Losses'] = merged['Losses'].astype(int)
    
    rounds = ['FR', 'CF', 'F']
    fig, axes = plt.subplots(3, 1, figsize=(12, 16))
    
    for i, rnd in enumerate(rounds):
        sub = merged[merged['round'] == rnd].copy()
        sub = sub.sort_values('Wins', ascending=False)
        
        x = np.arange(len(sub))
        width = 0.35
        
        axes[i].bar(x - width/2, sub['Wins'], width, label='Wins')
        axes[i].bar(x + width/2, sub['Losses'], width, label='Losses')
        
        axes[i].set_xticks(x)
        axes[i].set_xticklabels(sub['team'])
        axes[i].set_ylabel('Games')
        axes[i].set_title(f"{rnd} Round — Wins vs Losses by Team")
        axes[i].legend()
        axes[i].grid(axis='y', linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.show()


def playoff_teams():
    df = sd.series_post_df

    all_teams = pd.concat([
        df[['year', 'tmIDWinner']].rename(columns={'tmIDWinner': 'team'}),
        df[['year', 'tmIDLoser']].rename(columns={'tmIDLoser': 'team'})
    ])

    all_teams = all_teams.drop_duplicates(subset=['year', 'team'])

    appearances = all_teams['team'].value_counts().reset_index()
    appearances.columns = ['team', 'playoff_appearances']

    appearances = appearances.sort_values(by='playoff_appearances', ascending=False).reset_index(drop=True)


    return appearances