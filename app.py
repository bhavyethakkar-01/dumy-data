import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

st.set_page_config(page_title="Delhi Metro Dashboard", layout="wide")

st.markdown("""
    <style>
        .stApp {
            background-color: #0f1116;
            color: #ffffff;
        }
        h1, h2, h3, h4, h5, h6, p, div {
            color: #ffffff !important;
        }
        .block-container {
            padding-top: 1rem;
        }
        div[data-testid="stSidebar"] {
            background-color: #181a20;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("Delhi metro.csv")
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")
    return df

df = load_data()

# Add simulated columns for demo
np.random.seed(42)
df["total_users"] = np.random.randint(5000, 100000, len(df))
df["total_sessions"] = np.random.randint(1000, 50000, len(df))
df["avg_sessions_per_user"] = (df["total_sessions"] / df["total_users"]).round(2)
df["Passenger_Count"] = np.random.randint(500, 10000, len(df))
df["Hour"] = np.random.randint(0, 24, len(df))
df["Active_Users"] = np.random.randint(1000, 30000, len(df))

top10_stations = df.nlargest(10, "total_users")
top_routes = df.sample(10).copy()
top_routes["From_Station"] = np.random.choice(df["Station_Names"], 10)
top_routes["To_Station"] = np.random.choice(df["Station_Names"], 10)
top_routes["Usage_Score"] = np.random.randint(100, 1000, 10)
peak_hour = df.groupby("Hour")["Passenger_Count"].sum().reset_index()
top10_peak = df.nlargest(10, "Passenger_Count")
daily_active = pd.DataFrame({
    "Date": pd.date_range("2024-01-01", periods=30),
    "Active_Users": np.random.randint(500, 30000, 30)
})

st.sidebar.title("Delhi Metro Dashboard")
page = st.sidebar.radio("Navigate", [
    "Dashboard Overview",
    "Metro Maps",
    "Peak Hour Analysis",
    "Active Users Trend"
])

def dark_fig(fig, x_title, y_title):
    fig.update_layout(
        plot_bgcolor="#0f1116",
        paper_bgcolor="#0f1116",
        font=dict(color="#FFFFFF", size=13),
        xaxis=dict(title=x_title, color="#FFFFFF", showgrid=True, gridcolor="#333333"),
        yaxis=dict(title=y_title, color="#FFFFFF", showgrid=True, gridcolor="#333333"),
        title_font=dict(size=22, color="#FFFFFF"),
        margin=dict(l=60, r=40, t=80, b=60)
    )
    return fig

if page == "Dashboard Overview":
    st.title("Delhi Metro Data Dashboard")

    total_users = df["total_users"].sum()
    total_sessions = df["total_sessions"].sum()
    avg_sessions = df["avg_sessions_per_user"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", f"{total_users:,}")
    col2.metric("Total Sessions", f"{total_sessions:,}")
    col3.metric("Avg Sessions per User", f"{avg_sessions:.2f}")

    st.subheader("Total Users per Metro Line")
    fig_users = px.bar(df, x="Metro_Line", y="total_users", color="total_users",
                       color_continuous_scale="Blues", title="Total Users per Metro Line")
    st.plotly_chart(dark_fig(fig_users, "Metro Line", "Total Users"), use_container_width=True)

    st.subheader("Total Sessions per Metro Line")
    fig_sessions = px.bar(df, x="Metro_Line", y="total_sessions", color="total_sessions",
                          color_continuous_scale="Greens", title="Total Sessions per Metro Line")
    st.plotly_chart(dark_fig(fig_sessions, "Metro Line", "Total Sessions"), use_container_width=True)

    st.subheader("Average Sessions per User")
    fig_avg = px.bar(df, x="Metro_Line", y="avg_sessions_per_user", color="avg_sessions_per_user",
                     color_continuous_scale="Oranges", title="Average Sessions per User by Metro Line")
    st.plotly_chart(dark_fig(fig_avg, "Metro Line", "Avg Sessions/User"), use_container_width=True)

elif page == "Metro Maps":
    st.title("Metro Maps and Heatmap")

    # st.subheader("Top 10 Metro Stations (By Users)")
    # m1 = folium.Map(location=[df["Latitude"].mean(), df["Longitude"].mean()],
    #                 zoom_start=11, tiles="CartoDB positron")
    # valid_stations = top10_stations.dropna(subset=["Latitude", "Longitude"])
    # for _, row in valid_stations.iterrows():
    #     folium.CircleMarker(
    #         location=[row["Latitude"], row["Longitude"]],
    #         radius=7,
    #         color="orange",
    #         fill=True,
    #         fill_color="orange",
    #         popup=f"{row['Station_Names']}<br>Users: {row['total_users']}"
    #     ).add_to(m1)
    # st_folium(m1, width=900, height=500)

    st.subheader("Top 10 Used Routes")
    fig_routes = px.bar(top_routes,
                        x=top_routes["From_Station"] + " → " + top_routes["To_Station"],
                        y="Usage_Score", color="Usage_Score",
                        color_continuous_scale="Viridis", title="Top 10 Most Used Routes")
    st.plotly_chart(dark_fig(fig_routes, "Route", "Usage Score"), use_container_width=True)

    st.subheader("Heatmap of Metro User Density")
    heat_df = df.dropna(subset=["Latitude", "Longitude"])
    if not heat_df.empty:
        m2 = folium.Map(location=[df["Latitude"].mean(), df["Longitude"].mean()],
                        zoom_start=11, tiles="CartoDB positron")
        heat_data = list(zip(heat_df["Latitude"], heat_df["Longitude"], heat_df["total_users"]))
        HeatMap(heat_data, radius=12, blur=15, min_opacity=0.4,
                gradient={0.4: "yellow", 0.65: "orange", 1: "red"}).add_to(m2)
        st_folium(m2, width=900, height=500)

elif page == "Peak Hour Analysis":
    st.title("Peak Hour Analysis")

    st.subheader("Passenger Count by Hour")
    fig_peak = px.line(peak_hour, x="Hour", y="Passenger_Count", markers=True,
                       color_discrete_sequence=["#00CC96"], title="Passenger Flow Across the Day")
    st.plotly_chart(dark_fig(fig_peak, "Hour", "Passenger Count"), use_container_width=True)

    st.subheader("Top 10 Stations During Peak Hour")
    fig_top_peak = px.bar(top10_peak, x="Station_Names", y="Passenger_Count",
                          color="Passenger_Count", color_continuous_scale="Reds",
                          title="Top 10 Stations by Peak Hour Load")
    st.plotly_chart(dark_fig(fig_top_peak, "Station", "Passenger Count"), use_container_width=True)

elif page == "Active Users Trend":
    st.title("Daily Active Users Trend")
    fig_active = px.line(daily_active, x="Date", y="Active_Users", markers=True,
                         color_discrete_sequence=["#1f77b4"], title="Daily Active Users Over Time")
    st.plotly_chart(dark_fig(fig_active, "Date", "Active Users"), use_container_width=True)
