from data_scripts import _store_data as sd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

def clean_no_pos_players():
     sd.players_df = sd.players_df[sd.players_df['pos'].notna() & (sd.players_df['pos'] != "")]

def clean_no_bd_players():
     sd.players_df = sd.players_df[sd.players_df['pos'].notna() & (sd.players_df['birthDate'] != "0000-00-00")]


def birthDate_check():
     df = sd.players_df.copy()
     df['birthDate_parsed'] = pd.to_datetime(df['birthDate'], errors='coerce')
     df['birthYear'] = df['birthDate_parsed'].dt.year.fillna(0).astype(int)

     plt.figure(figsize=(18, 6))
     plt.scatter(df.index, df['birthYear'], alpha=0.6)

     plt.title("Scatter Plot of Player Birth Years (including invalid 0000-00-00)")
     plt.xlabel("Player Index")
     plt.ylabel("Birth Year")
     plt.grid(True)

     invalid_mask = df['birthYear'] == 0
     if invalid_mask.any():
          plt.scatter(df.index[invalid_mask], np.zeros(invalid_mask.sum()), color='red', label='Invalid Dates')
          plt.legend()

     plt.show()


def normalize_players():
     df = sd.players_df.copy()

     df['primary_pos'] = df['pos'].str[0]

     for pos in df['primary_pos'].unique():
          pos_mask = df['primary_pos'] == pos
          df_pos = df[pos_mask]

          Q1_h, Q3_h = df_pos['height'].quantile([0.25, 0.75])
          IQR_h = Q3_h - Q1_h
          lower_h, upper_h = Q1_h - 1.5 * IQR_h, Q3_h + 1.5 * IQR_h
          mean_h = df_pos['height'].mean()

          Q1_w, Q3_w = df_pos['weight'].quantile([0.25, 0.75])
          IQR_w = Q3_w - Q1_w
          lower_w, upper_w = Q1_w - 1.5 * IQR_w, Q3_w + 1.5 * IQR_w
          mean_w = df_pos['weight'].mean()

          df['height'] = df['height'].astype(float)
          df.loc[pos_mask & (df['height'] < lower_h), 'height'] = mean_h
          df.loc[pos_mask & (df['height'] > upper_h), 'height'] = mean_h

          df.loc[pos_mask & (df['weight'] < lower_w), 'weight'] = mean_w
          df.loc[pos_mask & (df['weight'] > upper_w), 'weight'] = mean_w

     df.drop(columns=['primary_pos'], inplace=True)

     sd.players_df = df

     
def college_origin():
     df = sd.players_df.copy()
     df["college_status"] = df["college"].apply(lambda x: "No College" if pd.isna(x) or x.strip() == "" else "College")
     
     college_counts = df["college_status"].value_counts()
     
     plt.figure(figsize=(18, 6))
     college_counts.plot(kind="bar", color=["#1f77b4", "#ff7f0e"])
     plt.title("Players With vs Without College")
     plt.xlabel("College Status")
     plt.ylabel("Number of Players")
     plt.xticks(rotation=0)
     plt.tight_layout()
     plt.show()


def top_10_colleges_table():
    df = sd.players_df.copy()
    college_counts = df["college"].value_counts().reset_index()
    college_counts.columns = ["College", "Number of Players"]
    
    top_10 = college_counts.head(10)
    return top_10

def players_by_position():
     df = sd.players_df.copy()
     pos_counts = df["pos"].value_counts()
     
     plt.figure(figsize=(18, 6))
     pos_counts.plot(kind="bar", color="#1f77b4", edgecolor="black")
     plt.title("Number of Players by Position")
     plt.xlabel("Position")
     plt.ylabel("Number of Players")
     plt.xticks(rotation=0)
     
     for i, count in enumerate(pos_counts):
          plt.text(i, count + 1, str(count), ha="center", va="bottom", fontsize=9)
     
     plt.tight_layout()
     plt.show()

def position_merge():
    order = ['C', 'F', 'G']

    def map_position(pos):
        if pd.isna(pos) or pos.strip() == "":
            return None
        pos_clean = pos.replace("-", "").replace(" ", "").upper()
        letters = [p for p in order if p in pos_clean]
        return ''.join(letters) if letters else None

    sd.players_df['pos'] = sd.players_df['pos'].apply(map_position)

def position_height_weight():
     df = sd.players_df.copy()
     fig = px.scatter_3d(
          df,
          x='pos',
          z='height',
          y='weight',
          color='pos',
          symbol='pos',
          hover_data=['bioID', 'college'],
          title='3D Correlation Between Position, Height, and Weight',
          height=500,
          width=1000
     )

     fig.update_traces(marker=dict(size=5, opacity=0.8))
     fig.update_layout(
          scene=dict(
               xaxis_title='Position',
               yaxis_title='Weight (lbs)',
               zaxis_title='Height (inches)',
               domain=dict(x=[0, 1], y=[0, 1])
          ),
          margin=dict(l=0, r=0, b=0, t=50)
     )

     fig.show()