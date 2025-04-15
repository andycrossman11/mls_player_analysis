import pandas as pd
import numpy as np

class MLSPlayerAnalysis():
    def __init__(self, mls_df_path: str):
        self.mls_ds = preprocess_data(mls_df_path)
        
    def build_position_scores(self) -> dict[str, pd.DataFrame]:
        
        self.position_dfs: dict[str, pd.DataFrame] = initialize_position_dfs(self.mls_ds)

        self.position_statistics: dict[str, dict[str, float]] = compute_position_statistics(self.position_dfs)

        standardize_columns(self.position_dfs, self.position_statistics)
        compute_efficiency(self.position_dfs)
        compute_potential(self.position_dfs)
        compute_value(self.position_dfs)

        return self.position_dfs
    
def preprocess_data(mls_data_path: str) -> pd.DataFrame:
    """Preprocess the dataset (IN-PLACE) by:
    1. Dropping id & second_position columns
    2. Filtering out goalkeepers
    3. Converting minutes played to numeric
    4. Calculating # of 90 minutes played (stored in 90_minutes_played)
    """
    df: pd.DataFrame = pd.read_csv(mls_data_path)
    print(df.columns)
    df.drop(columns=["id", "second_position"], inplace=True)
    df = df[df['position'] != "Keeper"]
    df['minutes_played'] = df['minutes_played'].str.replace(',', '').astype(float)
    df['90_minutes_played'] = df['minutes_played'] / 90
    return df

def initialize_position_dfs(mls_ds: pd.DataFrame) -> dict[str, pd.DataFrame]:
    position_dfs = {position: mls_ds[mls_ds['position'] == position] for position in mls_ds['position'].unique()}
    
    for position, df in position_dfs.items():
        df['goals_per_90'] = df['goals'] / df['90_minutes_played']
        df['assists_per_90'] = df['assists'] / df['90_minutes_played']
        position_dfs[position] = df  # Update the dictionary with the modified DataFrame

    return position_dfs

def compute_position_statistics(position_dfs: dict[str, pd.DataFrame]) -> dict[str, dict[str, float]]:
    stats = {}
    for position, df in position_dfs.items():
        stats[position] = {
            'goals_per_90_mean': df['goals_per_90'].mean(),
            'goals_per_90_std': df['goals_per_90'].std(),
            'assists_per_90_mean': df['assists_per_90'].mean(),
            'assists_per_90_std': df['assists_per_90'].std()
        }
    print(stats)
    return stats

def standardize_columns(position_dfs: dict[str, pd.DataFrame], position_stats: dict[str, dict[str, float]]) -> None:
    for position, df in position_dfs.items():
        df['goals_per_90_z'] = (df['goals_per_90'] - position_stats[position]['goals_per_90_mean']) / position_stats[position]['goals_per_90_std']
        df['assists_per_90_z'] = (df['assists_per_90'] - position_stats[position]['assists_per_90_mean']) / position_stats[position]['assists_per_90_std']
        position_dfs[position] = df 

def compute_efficiency(position_dfs: dict[str, pd.DataFrame]) -> None:
    for position, df in position_dfs.items():
        unscaled_efficiency = df['goals_per_90_z'] + (0.5 * df['assists_per_90_z'])
        df['player_efficiency'] = (unscaled_efficiency - unscaled_efficiency.min()) / (unscaled_efficiency.max() - unscaled_efficiency.min())
        position_dfs[position] = df 

def compute_potential(position_dfs: dict[str, pd.DataFrame]) -> None:
    for position, df in position_dfs.items():
        df['player_potential'] = 1 / (1 + np.exp((df['age'] - 28) / 3))
        position_dfs[position] = df  

def compute_value(position_dfs: dict[str, pd.DataFrame]) -> None:
    for position, df in position_dfs.items():
        df['player_value'] = 0.7 * df['player_efficiency'] + 0.3 * df['player_potential']
        position_dfs[position] = df.sort_values(by='player_value', ascending=False, inplace=True)
        position_dfs[position] = df[['name', 'age', 'player_efficiency', 'player_potential', 'player_value']].reset_index(drop=True).head(10)

