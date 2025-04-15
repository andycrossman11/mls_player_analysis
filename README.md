# MLS Player Valuation
    - A 2024 MLS player dataset was split by position group - **Defender, Midfielder, Forward**.
    - Within each position, the player value formula is based on a combination of **player efficiency** and **potential**.
    - The formula is designed to provide a comprehensive view of a player's current performance and future potential **relative to their position group.**

## Environment Setup
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r src/requirements.txt

## EDA
- Look at eda.ipynb for a look at just the formula code for player evaluation

## Streamlit Dashboard
- streamlit run src/mls_data_visualization.py

## Data Source
- https://www.kaggle.com/datasets/flynn28/mls-player-stats-database