import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
athletes_df = pd.read_csv('athlete_events.csv')

# Data preprocessing
medal_data = athletes_df[athletes_df['Medal'].notna()]
noc_list = ["None"] + sorted(medal_data['NOC'].unique().tolist())
year_list = ["None"] + sorted(athletes_df['Year'].unique().tolist())
sport_list = ["None"] + sorted(athletes_df['Sport'].unique().tolist())

# Streamlit UI
st.set_page_config(page_title="Olympics Dashboard", layout="wide")
st.title("🏅 Olympics Dashboard (1896 - 2016)")

# Sidebar Filters
st.sidebar.header("Data Filters")
selected_country = st.sidebar.selectbox("Select Country", noc_list, index=0)
selected_years = st.sidebar.multiselect("Select Year", year_list)
selected_sports = st.sidebar.multiselect("Select Sport", sport_list)
age_range = st.sidebar.slider("Select Age Range", min_value=10, max_value=50, value=(10, 50))
st.sidebar.header("Data Visualizations")
display_chart = st.sidebar.selectbox("Select Visualization", ["None", "Choropleth Map", "Sports Over Time", "Medal Distribution", "Age Distribution"])

# Filter data
filtered_data = athletes_df.copy()
if selected_country != "None":
    filtered_data = filtered_data[filtered_data["NOC"] == selected_country]
if selected_years:
    filtered_data = filtered_data[filtered_data["Year"].astype(int).isin(selected_years)]
if selected_sports:
    filtered_data = filtered_data[filtered_data["Sport"].isin(selected_sports)]
filtered_data = filtered_data[(filtered_data["Age"] >= age_range[0]) & (filtered_data["Age"] <= age_range[1])]

# Display Filtered Count
st.sidebar.markdown(f"**Showing {len(filtered_data)} results**")

# Data Table
st.subheader("Filtered Data Table")
expand_table = st.checkbox("Show More Rows", value=False)
data_table_rows = 50 if expand_table else 20
st.dataframe(filtered_data.head(data_table_rows))

# Download Filtered Data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

download_csv = convert_df(filtered_data)
st.download_button(label="Download Data", data=download_csv, file_name="filtered_data.csv", mime="text/csv")

# Visualizations
year_slider = st.slider("Select Year", min_value=int(athletes_df['Year'].min()), max_value=int(athletes_df['Year'].max()), value=int(athletes_df['Year'].max()), step=4)

fig = None

if display_chart == "Choropleth Map":
    filtered_medal_data = athletes_df[(athletes_df['Medal'].notna()) & (athletes_df['Year'] == year_slider)]
    medal_counts = filtered_medal_data.groupby("NOC").size().reset_index(name="count")
    fig = px.choropleth(medal_counts, locations="NOC", locationmode="ISO-3", color="count", 
                        title="Overall Country-wise Medal Count", color_continuous_scale=px.colors.sequential.Plasma, width=1200, height=800)

elif display_chart == "Sports Over Time":
    sport_options = st.multiselect("Select Sports to Compare", sport_list, default=[sport_list[1] if len(sport_list) > 1 else sport_list[0]])
    filtered_participation = athletes_df[athletes_df['Sport'].isin(sport_options)]
    participation = filtered_participation.groupby("Year").size().reset_index(name="Athlete Count")
    fig = px.line(participation, x="Year", y="Athlete Count", title="Sports Participation Over Time",
                color_discrete_sequence=px.colors.qualitative.Set1, markers=True)

if display_chart == "Medal Distribution":
    selected_medal_country = st.selectbox("Select Country for Medal Insights", ["All"] + sorted(medal_data['NOC'].unique().tolist()))
    if selected_medal_country != "All":
        country_medal_data = athletes_df[(athletes_df['Medal'].notna()) & (athletes_df['NOC'] == selected_medal_country)]
    else:
        country_medal_data = athletes_df[athletes_df['Medal'].notna()]
    medal_counts = country_medal_data["Medal"].value_counts()
    fig = px.bar(medal_counts, x=medal_counts.index, y=medal_counts.values, 
                title="Medal Distribution", labels={"x": "Medal Type", "y": "Count"}, 
                color=medal_counts.index, color_discrete_sequence=px.colors.qualitative.Bold)

if display_chart == "Age Distribution":
    filtered_age_data = athletes_df[athletes_df['Age'].notna()]
    fig = px.histogram(filtered_age_data, x="Age", title="Age Distribution of Athletes", nbins=50, color_discrete_sequence=["#ff7f0e"])

if fig:
    st.plotly_chart(fig, use_container_width=True, key=f"{display_chart}_chart")
else:
    st.warning("No data available for the selected filters. Try adjusting your selection.")
