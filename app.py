import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
athletes_df = pd.read_csv("athlete_events.csv")

# Data preprocessing
medal_data = athletes_df[athletes_df['Medal'].notna()]
noc_list = ["None"] + sorted(medal_data['NOC'].unique().tolist())
year_list = sorted(athletes_df['Year'].unique().tolist())
sport_list = sorted(athletes_df['Sport'].unique().tolist())

# Streamlit UI Configuration
st.set_page_config(page_title="Olympics Dashboard", layout="wide")

# Dashboard Title
st.title("🏅 Olympics Dashboard (1896 - 2016)")

# Creating Two Tabs with Extended Width
col1, col2 = st.columns(2)
with col1:
    tab1_button = st.button("📊 Visualizations", use_container_width=True)
with col2:
    tab2_button = st.button("📋 Data Filtering", use_container_width=True)

# Toggle between tabs based on button clicks
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Visualizations"
if tab1_button:
    st.session_state.active_tab = "Visualizations"
if tab2_button:
    st.session_state.active_tab = "Data Filtering"

# Sidebar Filters (apply to both tabs)
st.sidebar.header("Filters")
selected_country = st.sidebar.selectbox("Select Country", ["None"] + noc_list, index=0)
selected_years = st.sidebar.multiselect("Select Year", year_list, default=[])
selected_sports = st.sidebar.multiselect("Select Sport", sport_list, default=[])
age_range = st.sidebar.slider("Select Age Range", min_value=10, max_value=50, value=(10, 50))

# Visualization Selection
display_chart = st.sidebar.selectbox("Select Visualization", 
                                     ["None", "🌍 Global Medal Distribution", "📈 Athlete Participation Trends", "🏅 Medal Breakdown", "📊 Athlete Age Analysis"])

# Filter Data (ensuring filters apply to all visualizations)
filtered_data = athletes_df.copy()
if selected_country != "None":
    filtered_data = filtered_data[filtered_data["NOC"] == selected_country]
if selected_years:
    filtered_data = filtered_data[filtered_data["Year"].astype(int).isin(selected_years)]
if selected_sports:
    filtered_data = filtered_data[filtered_data["Sport"].isin(selected_sports)]
filtered_data = filtered_data[(filtered_data["Age"] >= age_range[0]) & (filtered_data["Age"] <= age_range[1])]

# Sidebar Filtered Count
st.sidebar.markdown(f"**Showing {len(filtered_data)} results**")

# --------------------- 📊 Visualization Tab ---------------------
if st.session_state.active_tab == "Visualizations":
    st.subheader("Visualizations")

    if display_chart == "None":
        # Default Information (Olympic Summary)
        st.markdown("### Welcome to the Olympics Dashboard!")
        st.write("Use the filters on the left to explore various aspects of the Olympic Games from 1896 to 2016.")

        # Summary Statistics
        total_editions = athletes_df["Year"].nunique()
        total_host_cities = athletes_df["City"].nunique()
        total_medals = medal_data.shape[0]
        total_athletes = athletes_df["ID"].nunique()
        total_nations = athletes_df["NOC"].nunique()
        total_sports = athletes_df["Sport"].nunique()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏟 Total Olympic Editions", total_editions)
            st.metric("🌍 Total Host Cities", total_host_cities)
        with col2:
            st.metric("🏅 Total Medals Awarded", total_medals)
            st.metric("🏃‍♂️ Total Athletes Participated", total_athletes)
        with col3:
            st.metric("🏆 Total Nations Participated", total_nations)
            st.metric("⚽ Total Sports Held", total_sports)

        # Default Chart: Participation Trends Over Time
        #participation_trends = athletes_df.groupby("Year").size().reset_index(name="Athlete Count")
        #fig = px.line(participation_trends, x="Year", y="Athlete Count", 
        #             title="Olympic Participation Trends Over Time", 
        #            markers=True, color_discrete_sequence=["#ff7f0e"])
        #st.plotly_chart(fig, use_container_width=True)

    else:
        fig = None
        if display_chart == "🌍 Global Medal Distribution":
            filtered_medal_data = filtered_data[filtered_data['Medal'].notna()]
            medal_counts = filtered_medal_data.groupby("NOC").size().reset_index(name="count")
            fig = px.choropleth(medal_counts, locations="NOC", locationmode="ISO-3", color="count",
                                title="Overall Country-wise Medal Count", color_continuous_scale=px.colors.sequential.Plasma, width=1000, height=600)

        elif display_chart == "📈 Athlete Participation Trends":
            filtered_participation = filtered_data[filtered_data['Sport'].notna()]
            participation = filtered_participation.groupby("Year").size().reset_index(name="Athlete Count")
            fig = px.line(participation, x="Year", y="Athlete Count", title="Sports Participation Over Time",
                          color_discrete_sequence=px.colors.qualitative.Set1, markers=True)

        elif display_chart == "🏅 Medal Breakdown":
            # Medal Bar Chart
            medal_counts = filtered_data["Medal"].value_counts()
            medal_bar_chart = px.bar(medal_counts, x=medal_counts.index, y=medal_counts.values, 
                                     title="Medal Distribution", labels={"x": "Medal Type", "y": "Count"}, 
                                     color=medal_counts.index, color_discrete_sequence=px.colors.qualitative.Bold)

            # Medal Share Donut Chart
            team_medal_counts = medal_data.groupby("NOC")["Medal"].count().reset_index()
            team_medal_counts.columns = ["Team", "Total Medals"]
            team_medal_counts = team_medal_counts.sort_values(by="Total Medals", ascending=False)
            top_teams = team_medal_counts[:15]
            others_sum = team_medal_counts[15:]["Total Medals"].sum()
            others_row = pd.DataFrame({"Team": ["Others"], "Total Medals": [others_sum]})
            final_medal_counts = pd.concat([top_teams, others_row])

            donut_fig = px.pie(final_medal_counts, names="Team", values="Total Medals", 
                               title="Medal Share of Top 15 Teams", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)

            st.plotly_chart(medal_bar_chart, use_container_width=True, key="medal_bar_chart")
            st.plotly_chart(donut_fig, use_container_width=True, key="medal_donut_chart")

        elif display_chart == "📊 Athlete Age Analysis":
            fig = px.histogram(filtered_data, x="Age", title="Age Distribution of Athletes", nbins=50, color_discrete_sequence=["#ff7f0e"])

        if fig:
            st.plotly_chart(fig, use_container_width=True)

# --------------------- 📋 Data Filtering Tab ---------------------
if st.session_state.active_tab == "Data Filtering":
    st.subheader("Filtered Data Table")
    expand_table = st.checkbox("Show More Rows", value=False)
    data_table_rows = 50 if expand_table else 20
    st.dataframe(filtered_data.head(data_table_rows))

    # Download Filtered Data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    download_csv = convert_df(filtered_data)
    st.download_button(label="📥 Download Data", data=download_csv, file_name="filtered_data.csv", mime="text/csv")
