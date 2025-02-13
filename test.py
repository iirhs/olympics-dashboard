from shiny import App, reactive, render, ui
import pandas as pd
import plotly.express as px

# Load the dataset
df = pd.read_csv('athlete_events.csv')

# Data preprocessing
medal_data = df[df['Medal'].notna()]
noc_list = ["None"] + sorted(medal_data['NOC'].unique().tolist())
year_list = ["None"] + sorted(df['Year'].unique().tolist())
sport_list = ["None"] + sorted(df['Sport'].unique().tolist())

# Define UI
app_ui = ui.page_fluid(
    # Add custom CSS styles
    ui.tags.style(
        """
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
        }
        .sidebar {
            background-color: #ffffff;
            border-right: 2px solid #cccccc;
            padding: 15px;
            box-shadow: 2px 0px 5px rgba(0,0,0,0.1);
        }
        .main-panel {
            padding: 20px;
            background-color: #ffffff;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
            border-radius: 10px;
        }
        .title {
            color: #3a87ad;
            text-align: center;
            margin-bottom: 20px;
            font-size: 24px;
            font-weight: bold;
        }
        .btn {
            background-color: #3a87ad;
            color: white;
            border: none;
            padding: 8px 16px;
            cursor: pointer;
            border-radius: 5px;
        }
        .btn:hover {
            background-color: #2d6e8e;
        }
        """
    ),
    ui.row(
        ui.column(
            3,  # Sidebar width
            ui.tags.div(
                ui.input_selectize("selected_country", "Select Country", noc_list, multiple=False),
                ui.input_selectize("year", "Select Year", year_list, multiple=True),
                ui.input_selectize("sport", "Select Sport", sport_list, multiple=True),                
                ui.input_selectize("athlete_name", "Search Athlete by Name", choices=["None"], multiple=False),
                ui.input_slider("age", "Select Age Range", min=10, max=50, value=(20, 30)),
                ui.input_radio_buttons(
                    "plot_type",
                    "Select Plot Type",
                    ["None", "Age vs Medal Achievement", "Height vs Sport", "Year vs Medal Count", "Team vs Medal Distribution"]
                ),
                ui.div(
                    ui.input_action_button("clear_filters", "Clear Filters", class_="btn", style="margin-right: 10px;"),
                    ui.input_action_button("apply_filters", "Apply Filters", class_="btn", style="margin-left: 10px;")
                ),            
                class_="sidebar"
            )
        ),
        ui.column(
            9,  # Main panel width
            ui.tags.div(
                ui.tags.h1("Olympics (1896 - 2016)", class_="title"),
                ui.output_table("country_details"),
                ui.output_table("athlete_details"),
                ui.div(
                    ui.output_ui("correlation_plot"),
                    class_="main-panel"
                )
            )
        )
    )
)

def server(input, output, session):
    @output
    @render.table
    def country_details():
        if input.selected_country() and input.selected_country() != "None":
            country_data = df[df["NOC"] == input.selected_country()]
            return country_data[["Name", "Age", "Height", "Weight", "Sport", "Medal", "Year"]]
        return None

    @output
    @render.table
    def athlete_details():
        if input.athlete_name() and input.athlete_name() != "None":
            athlete_data = df[df["Name"] == input.athlete_name()]
            return athlete_data[["Name", "Age", "Height", "Weight", "Sport", "Medal", "Year"]]
        return None

    @output
    @render.ui
    def correlation_plot():
        if input.plot_type() == "None":
            return ui.HTML("<p>Select a plot type to display visualization.</p>")

        current_filters = {
            "country": input.selected_country(),
            "year": input.year(),
            "sport": input.sport(),
            "age": input.age()
        }
        
        filtered_data = medal_data[
            (medal_data['NOC'] == current_filters["country"] if current_filters["country"] != "None" else True) &
            (medal_data['Year'].isin(current_filters["year"]) if "None" not in current_filters["year"] else True) &
            (medal_data['Sport'].isin(current_filters["sport"]) if "None" not in current_filters["sport"] else True) &
            (medal_data['Age'] >= current_filters["age"][0]) &
            (medal_data['Age'] <= current_filters["age"][1])
        ]

        if filtered_data.empty:
            return ui.HTML("<p>No data to display. Adjust your filters.</p>")

        fig = None
        if input.plot_type() == "Age vs Medal Achievement":
            age_data = filtered_data.groupby("Age").size().reset_index(name="Count")
            fig = px.scatter(age_data, x="Age", y="Count", title="Age vs Medal Achievement")
        elif input.plot_type() == "Height vs Sport":
            fig = px.box(filtered_data, x="Sport", y="Height", color="Sex", title="Height vs Sport")
        elif input.plot_type() == "Year vs Medal Count":
            yearly_data = filtered_data.groupby("Year").size().reset_index(name="Count")
            fig = px.line(yearly_data, x="Year", y="Count", title="Year vs Medal Count")
        elif input.plot_type() == "Team vs Medal Distribution":
            team_data = filtered_data.groupby("NOC").size().reset_index(name="Count")
            fig = px.choropleth(team_data, locations="NOC", locationmode="ISO-3", color="Count", title="Team vs Medal Distribution")

        return ui.HTML(fig.to_html(full_html=False, include_plotlyjs="cdn")) if fig else ui.HTML("<p>No data to display.</p>")

app = App(app_ui, server)
