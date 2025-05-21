import numpy as np
from dash import dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc

country_map = {
            'USA': 'USA', 'UK': 'GBR', 'DR Congo': 'COD', 'Russia': 'RUS', 'Thailand': 'THA',
            'Colombia': 'COL', 'Egypt': 'EGY', 'Spain': 'ESP', 'Kenya': 'KEN', 'Japan': 'JPN',
            'Bangladesh': 'BGD', 'Nigeria': 'NGA', 'Pakistan': 'PAK', 'Myanmar': 'MMR',
            'South Africa': 'ZAF', 'Indonesia': 'IDN', 'Italy': 'ITA', 'Germany': 'DEU',
            'Brazil': 'BRA', 'Tanzania': 'TZA', 'South Korea': 'KOR', 'Turkey': 'TUR',
            'Vietnam': 'VNM', 'Iran': 'IRN', 'China': 'CHN', 'Mexico': 'MEX', 'India': 'IND',
            'Philippines': 'PHL', 'France': 'FRA', 'Ethiopia': 'ETH'
        }


def generate_geographic_map_figure(df_filtered, country_iso_map=country_map):
    df_processed = df_filtered.copy()
    df_processed['iso_alpha3'] = df_processed['Country'].map(country_iso_map)

    # Aggregate data
    agg_dict = {'Age': 'mean', 'Mortality_Risk': 'mean', '5_Year_Survival_Probability': 'mean', 'Country': 'count'}

    country_stats = df_processed.groupby(['Country', 'iso_alpha3', 'Continent'], observed=True).agg(agg_dict)
    country_stats = country_stats.rename(columns={'Country': 'Count'}).reset_index()

    hover_data_list = ['Age', 'Mortality_Risk', '5_Year_Survival_Probability']

    fig = px.scatter_geo(
        country_stats,
        locations='iso_alpha3',
        color='Continent',
        hover_name='Country',
        size='Count',
        hover_data=hover_data_list,
        projection='natural earth',
    )

    fig.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 0}, # t=30 leaves space for title if px adds one
        dragmode='select',  # Keep this if you want map selection to filter
        clickmode='event+select' # Important for callbacks listening to map clicks/selections
    )
    # To ensure the map respects the dcc.Graph height, clear any fixed height on the geo layout
    fig.update_geos(visible=True, resolution=110, scope="world",
                    bgcolor='rgba(0,0,0,0)', lakecolor='rgb(255, 255, 255)')
    return fig

def generate_smoking_risk_figure(df_filtered):
    fig = px.box(
        df_filtered,
        x='Smoking_Status',
        y='Mortality_Risk',
        title="Mortality Risk by Smoking Status",
        category_orders={"Smoking_Status": ['Non-Smoker', 'Former Smoker', 'Smoker']},
        labels = {'Smoking_Status': 'Smoking Status', 'Mortality_Risk': 'Mortality Risk (%)'}
    )

    fig.update_layout(
        margin=dict(l=50, r=20, t=40, b=40),
    )
    return fig

def generate_age_dist_figure(df_filtered):
    # Age Distribution
    fig = px.histogram(
        df_filtered,
        x="Age",
        #nbins=15,
        title="Patient Age Distribution (Histogram)",
        labels={'Age': 'Age', 'count': 'Number of Patients'},
        opacity=0.8
    )
    fig.update_layout(
        margin=dict(l=50, r=20, t=50, b=40),
        bargap=0.1
    )
    return fig

def generate_gender_pie_figure(df_filtered):
    # Gender Breakdown
    fig = px.pie(
        df_filtered.groupby('Gender', observed=True).size().reset_index(name='Count'),
        values='Count',
        names='Gender',
        title="Gender Distribution",
    )

    fig.update_layout(
        margin=dict(l=50, r=20, t=50, b=40),
        bargap=0.1
    )
    return fig

def generate_family_history_impact_figure(df_filtered):
    # Family History Impact
    fig = px.box(
        df_filtered,
        x="Family_History",
        y="5_Year_Survival_Probability",
        color="Family_History",
        title="Impact of Family History on Survival Probability",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(
        margin=dict(l=50, r=20, t=50, b=40),
        bargap=0.1
    )
    return fig

def generate_ses_figure(df_filtered):
    # SES vs. Cancer Stage
    fig = px.histogram(
        df_filtered,
        x="Socioeconomic_Status",
        color="Stage_at_Diagnosis",
        barmode='group',
        title="Cancer Stage by Socioeconomic Status",
        category_orders={"Socioeconomic_Status": ["Low", "Middle", "High"]},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        margin=dict(l=50, r=20, t=50, b=40),
        bargap=0.1
    )
    return fig



def generate_treatment_acces_figure(df_filtered):
    # Treatment Access vs. Survival
    fig = px.box(
        df_filtered,
        x="Treatment_Access",
        y="5_Year_Survival_Probability",
        color="Treatment_Access",
        title="5-Year Survival Probability by Treatment Access",
        category_orders={"Treatment_Access": ["None", "Partial", "Full"]},
    )
    fig.update_layout(
        margin=dict(l=50, r=20, t=50, b=40),
        bargap=0.1
    )
    return fig

def generate_kpi_cards(df_filtered):
    # --- Calculate KPI Values ---
    kpi_cards = []
    total_individuals = len(df_filtered)
    avg_mortality_risk = np.nanmean(df_filtered['Mortality_Risk']) * 100 if 'Mortality_Risk' in df_filtered else 0
    avg_survival_prob = np.nanmean(df_filtered['5_Year_Survival_Probability']) * 100 if '5_Year_Survival_Probability' in df_filtered else 0
    avg_age = np.nanmean(df_filtered['Age']) if 'Age' in df_filtered else 0

    kpi_cards.append(create_kpi_card("Total Individuals", f"{total_individuals:,}", "kpi-total-individuals"))
    kpi_cards.append(create_kpi_card("Avg. Mortality Risk", f"{avg_mortality_risk:.1f}%", "kpi-avg-mortality", color="danger" if avg_mortality_risk > 50 else "success"))
    kpi_cards.append(create_kpi_card("Avg. 5-Yr Survival", f"{avg_survival_prob:.1f}%", "kpi-avg-survival", color="success" if avg_survival_prob > 50 else "warning"))
    kpi_cards.append(create_kpi_card("Avg. Age", f"{avg_age:.1f}", "kpi-avg-age"))

    return kpi_cards

def create_kpi_card(title, value, card_id, color="primary", className="text-center"):
    return dbc.Col(
        dbc.Card(
            [
                dbc.CardHeader(title, className="text-center small fw-bold", style={'padding': '0.3rem 0.5rem'}),
                dbc.CardBody(
                    html.H4(value, className=f"card-title {className} my-1", id=card_id, style={'fontSize':'1.1rem'}),
                    style={'padding': '0.5rem'}
                )
            ], className="shadow-sm h-100"
        ), width=6, className="mb-2"
    )
