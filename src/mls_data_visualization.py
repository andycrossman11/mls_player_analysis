import streamlit as st
from mls_player_analysis import MLSPlayerAnalysis
import pandas as pd
import plotly.express as px

if "mls_data_analysis" not in st.session_state:
    mls_player_analysis = MLSPlayerAnalysis('2024 MLS Player Stats Database.csv')
    position_dfs: dict[str, pd.DataFrame] = mls_player_analysis.build_position_scores()
    st.session_state['mls_data_analysis'] = position_dfs

st.set_page_config(page_title="MLS Player Valuation Dashboard", layout="wide")
st.title("⚽ MLS Player Valuation Dashboard")
st.markdown(
    """
    ##### Developed by AJC
    - A 2024 MLS player dataset was split by position group - **Defender, Midfielder, Forward**.
    - Within each position, the player value formula is based on a combination of **player efficiency** and **potential**.
    - The formula is designed to provide a comprehensive view of a player's current performance and future potential **relative to their position group.**
    """
)

# --- Section: Explanation ---
with st.expander("📘 Formula Explanation", expanded=False):
    st.markdown(
        """
        ### Player Value Formula
        """
    )

    st.markdown(
        """
        -----
        ##### Player Efficiency Metric
        I calculate **player efficiency** as a weighted combination of standardized per-90 minute metrics (i.e., metrics per soccer match):
        """
    )

    st.latex(
        r"""
        \text{Efficiency} = z(\text{Goals per 90}) + \beta \cdot z(\text{Assists per 90})
        """
    )
    st.latex(
        r"""
        \text{Efficiency Score w/ Min Max} = \frac{\text{Efficiency} - \min(\text{Efficiency})}{\max(\text{Efficiency}) - \min(\text{Efficiency})}
        """
    )

    st.markdown(
        """
        Where:  
        - **z(...)** indicates standardization (z-score).  
        - **β** is the weight for assists, **which I set to .5** (i.e., 50% of the weight of goals).
        - **Min-Max Scaling** is used to ensure that the efficiency scores are confined to the interval [0, 1].
        """
    )

    st.markdown(
        """
        ---
        ##### Player Potential Metric
        **Potential** is a decreasing function of age (younger players with high efficiency are more valuable). This approach 
        is based on the idea that **players peak around age 28** and their potential declines thereafter.  
        
        The formula is given by:
        """
    )
    st.latex(r"""\text{Potential}(age) = \frac{1}{1 + e^{\frac{age - 28}{3}}}""")
    st.markdown(
        """
        Here:
        - **age** is the player's current age.
        - **28** is the assumed peak age.
        - **3** is a scaling factor determining how quickly potential declines around the peak age.
        - This function smoothly transitions from 1 (for younger players) toward 0 (for older players).
        """
    )

    st.markdown(
        """
        -----
        ##### Player Value Calculation
        We then combine the efficiency and potential metrics to compute the overall player value:
        """
    )

    st.latex(
        r"""
        \text{Player Value} = \alpha \cdot \text{Efficiency} + (1 - \alpha) \cdot \text{Potential}
        """
    )

    st.markdown(
        """
        Where:  
        - **α** is a tunable parameter and in the interval **[0, 1]**. This controls the weight between current performance and future potential.
        - I set **α = 0.7** to give more weight to current performance, but you can adjust this based on your preferences.
        """
    )


# --- Section: Visualizations ---
st.markdown("## 📊 Top Players by Position")

for position in st.session_state['mls_data_analysis']:
    st.markdown(f"### {position}s")

    df = st.session_state['mls_data_analysis'][position]
    top_players = df.sort_values(by="player_value", ascending=False).head(10)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Top 10 Players by Value**")
        st.dataframe(top_players[['name', 'player_value', 'player_efficiency', 'player_potential', 'age']])

    with col2:
        fig = px.scatter(
            top_players,
            x="player_efficiency",
            y="player_potential",
            size="player_value",
            color="age",
            hover_name="name",
            title=f"Top {position}s: Efficiency vs Potential",
            labels={
            "player_efficiency": "Efficiency",
            "player_potential": "Potential"
            }
        )
        fig.update_layout(
            xaxis=dict(range=[0, 1.1]),
            yaxis=dict(range=[0, 1.1])
        )
        st.plotly_chart(fig, use_container_width=True)

# --- Optional Footer ---
st.markdown("---")
st.caption("Developed by AJC — MLS Player Analytics | Dashboard powered by Python + Streamlit")
st.caption("Data Source: https://www.kaggle.com/datasets/flynn28/mls-player-stats-database")

