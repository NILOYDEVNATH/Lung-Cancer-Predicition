import numpy as np
from dash import Dash, dcc, html, Input, Output, State, dash
import pandas as pd
import dash_bootstrap_components as dbc

from tab_content import generate_geographic_map_figure, generate_smoking_risk_figure, generate_age_dist_figure, generate_gender_pie_figure, generate_family_history_impact_figure, generate_ses_figure, generate_treatment_acces_figure, generate_kpi_cards

CUSTOM_NA_VALUES = [
    '', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan',
    '1.#IND', '1.#QNAN', '<NA>', 'N/A', 'NA', 'NULL', 'NaN', 'n/a',
    'nan', 'null']

# Initialize the app
app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
# Load the real data
def load_real_data():
    # Load the real dataset

    df1 = pd.read_csv('lung_cancer_prediction.csv', keep_default_na=True)
    df1 = df1.replace(np.nan, 'None', regex=True)

    # Convert smoking status to an ordered category
    smoking_order = ['Non-Smoker', 'Former Smoker', 'Smoker']
    df1['Smoking_Status'] = pd.Categorical(df1['Smoking_Status'], categories=smoking_order, ordered=True)

    # Convert categorical strings to categories if needed
    for col in ['Cancer_Type', 'Mutation_Type', 'Socioeconomic_Status', 'Treatment_Access', 'Gender', 'Continent']:
        if df1[col].dtype == 'object':
            df1[col] = df1[col].astype('category')

    # Return the dataframe and other processed data
    return {
        'dataframe': df1,
        'countries': df1['Country'].unique().tolist(),
        'continents': df1['Continent'].unique().tolist(),
        'smoking_status': smoking_order,
        'cancer_types': df1['Cancer_Type'].unique().tolist(),
        'mutation_types': [mt for mt in df1['Mutation_Type'].unique() if pd.notna(mt)],
        'ages': df1['Age'],
        'genders': df1['Gender'].unique().tolist(),
        'family_history': df1['Family_History'].unique().tolist(),
        'treatment_access': df1['Treatment_Access'].unique().tolist(),
        'ses': df1['Socioeconomic_Status'].unique().tolist()
    }


# Get the real data
data = load_real_data()
df = data['dataframe']
df['AgeGroup'] = pd.cut(df['Age'], bins=10).astype(str)
df['Mortality_Risk_Bin'] = pd.cut(df['Mortality_Risk'], bins=10).astype(str)
df['Survival_Bin'] = pd.cut(df['5_Year_Survival_Probability'], bins=10).astype(str)
country_to_continent = df[['Country', 'Continent']].drop_duplicates().set_index('Country')['Continent'].to_dict()

color_theme = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'tertiary': '#2ca02c',
    'quaternary': '#d62728',
    'background': '#fafafa',
    'text': '#333333'
}

# --- App layout ---
app.layout = dbc.Container([
    # Header
    dbc.Row(
        dbc.Col(
            html.Div([
                html.H1("Lung Cancer Risk Analysis Dashboard",
                        style={
                            'textAlign': 'center',
                            'fontSize': '28px',
                            'color': color_theme['text'],
                            'fontWeight': 'bold'
                        })
            ], style={'backgroundColor': 'white','boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}
            )
        ), style={'height': '5vh', 'marginBottom': '1vh'}
    ),

    # Main Row: Sidebar + Content
    dbc.Row([
        # --- Sidebar Filters ---
        dbc.Col([
            # Sticky Title for Filters
            dbc.Row( # Sticky Title
                html.H4("🔍 Filter Data", className="mb-2 sticky-top bg-white py-2 text-center",
                        style={'fontSize': '1.1rem', 'color': color_theme['primary'], 'zIndex': 10, 'borderBottom': '1px solid #eee'}),
            ),
            dbc.Row([
                # --- Continent Filter ---
                dbc.Row([
                    html.Label("🌍 Continent", className="filter-label mb-1"),
                    dcc.Dropdown(
                        id='continent-filter',
                        options=[{'label': 'All', 'value': 'all'}] + [{'label': c, 'value': c} for c in data['continents']],
                        value='all',
                        className="dropdown"
                    )
                ], className="mb-2 filter-group", style={'height': '10vh'},),

                # --- Country Display (from map) ---
                dbc.Row([
                    html.Label("🗺️ Country (From Map)", className="filter-label mb-1"),
                    dcc.Store(id='map-filter-country', data='all'),
                    html.Div(id='selected-country-display', children="All Countries", className="filter-display-box")
                ], className="mb-2 filter-group", style={'height': '10vh'},),

                # --- Smoking Status and Cancer Type Filters ---
                dbc.Row([
                    dbc.Col([
                        html.Label("🚬 Smoking Status", className="filter-label mb-1"),
                        dcc.RadioItems(
                            id='smoking-filter',
                            options=[{'label': 'All', 'value': 'all'}] + [{'label': s, 'value': s} for s in data['smoking_status']],
                            value='all',
                            className="compact-radio",
                            labelClassName="compact-radio-label",
                            inputClassName="compact-radio-input"
                        ),
                    ]),
                    dbc.Col([
                        html.Label("🔬 Cancer Type", className="filter-label mb-1"),
                        dcc.RadioItems(
                            id='cancer-type-filter',
                            options=[{'label': 'All', 'value': 'all'}] + [{'label': ct, 'value': ct} for ct in data['cancer_types']],
                            value='all',
                            className="compact-radio",
                            labelClassName="compact-radio-label",
                            inputClassName="compact-radio-input"
                        )
                    ], style={'height': '100%'}),
                    dbc.Col([
                        html.Label("Family History", className="filter-label mb-1"),
                        dcc.RadioItems(
                            id='family-history-filter',
                            options=[{'label':'All','value':'all'}] + [{'label': ct, 'value': ct} for ct in data['family_history']],
                            value='all',
                            className="compact-radio",
                            labelClassName="compact-radio-label",
                            inputClassName="compact-radio-input"
                        )
                    ])
                ], className="mb-2 filter-group", style={'height': '15vh'},),

                # --- Gender Filter ---
                dbc.Row([
                    dbc.Col([
                        html.Label("👥 Gender:", className="filter-label mb-1"),
                        dcc.RadioItems(
                            id='sex-filter',
                            options=[{'label': 'All Genders', 'value': 'all'}] + [{'label': g, 'value': g} for g in data['genders']],
                            value='all',
                            className="compact-radio",
                            labelClassName="compact-radio-label",
                            inputClassName="compact-radio-input"
                    )
                    ]),
                    dbc.Col([
                        html.Label("Treatment Access:", className="filter-label mb-1"),
                        dcc.RadioItems(
                            id='treatment-access-filter',
                            options=[{'label': 'All', 'value': 'all'}] + [{'label': g, 'value': g} for g in data['treatment_access']],
                            value='all',
                            className="compact-radio",
                            labelClassName="compact-radio-label",
                            inputClassName="compact-radio-input"

                    )
                    ]),
                    dbc.Col([
                        html.Label("Socioeconomic Status", className="filter-label mb-1"),
                        dcc.RadioItems(
                            id='ses-filter',
                            options=[{'label': 'All', 'value': 'all'}] + [{'label': g, 'value': g} for g in data['ses']],
                            value='all',
                            className="compact-radio",
                            labelClassName="compact-radio-label",
                            inputClassName="compact-radio-input"
                    ),
                    ])

                ], className="mb-2 filter-group", style={'height': '12vh'}),
                html.Hr(className="my-2"),
                # --- Age Range Filter ---
                dbc.Row([
                    html.Label("🎂 Age Range", className="filter-label mb-1"),
                    dcc.RangeSlider(
                        id='age-range-slider',
                        min=int(data['ages'].min()) if not data['ages'].empty else 20, # Default min if data empty
                        max=int(data['ages'].max()) if not data['ages'].empty else 90, # Default max
                        value=[int(data['ages'].min()) if not data['ages'].empty else 20, int(data['ages'].max()) if not data['ages'].empty else 90],
                        marks={i: str(i) for i in range(int(data['ages'].min()) if not data['ages'].empty else 20, (int(data['ages'].max()) if not data['ages'].empty else 90) + 1, 10)},
                        step=1,
                        tooltip={"placement": "bottom", "always_visible": False},
                    )
                ], className="filter-group", style={'height': '8vh'},),

                # --- Reset Button ---
                dbc.Row(
                    html.Button('Reset All Filters', id='reset-filters-button', n_clicks=0,
                                className='btn btn-outline-danger btn-sm w-100 mt-2'), # Changed color, full width
                    className="pt-2", style={'height': '8vh'},
                )

            ], style={
                'padding': '10px',
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.05)',
                'height': 'calc(100% - 40px)',
                'overflowY': 'hidden'
            })
        ],
        width=12, lg=3, # Sidebar column width
        style={
            'height': '100%', # Takes full height of its parent row (94vh)
            'paddingRight': '0px',
            'paddingLeft': '0px' # No left padding for the column itself
        }
        ),
        # --- Main Content Area with Thematic Zones ---
        # --- Main content ---
        dbc.Col([
            # --- Zone 1: Geographic & Key KPIs ---
            dbc.Row([
                dbc.Col([
                    dbc.Row(id='kpi-cards-output', style={'height': '100%'}), # For KPI cards
                ], md=4, className="zone-container", style={'height': '100%'}),
                dbc.Col([
                    html.Div([
                        html.P([
                            "The map shows lung cancer patterns worldwide. Different healthcare systems and environmental factors can affect outcomes."
                        ], className="text-muted mb-1")
                    ], className="px-2"),
                    # html.H5("Geographic Distribution & KPIs", className="zone-title"),
                    dcc.Graph(id='map-graph-output', style={'height': '100%'}) # Map
                ], md=8, className="zone-container", style={'height': '100%'}) # Full width within this content column for this zone
            ], style={'height': '36vh', 'marginBottom': '1vh'}),

            # --- Zone 2: Risk Factors Analysis ---
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.P([
                            "Smoking influences lung cancer mortality risk."
                        ], className="text-muted mb-1")
                    ], className="px-2"),
                    #html.H5("Risk Factors Analysis", className="zone-title"),
                    dcc.Graph(id='smoking-risk-graph-output') # Smoking chart
                ], md=4, className="zone-container"), # Third width
                dbc.Col([
                    html.Div([
                        html.P([
                            "Age distribution of patients."
                        ], className="text-muted mb-1")
                    ], className="px-2"),
                    #html.H5("Age & Gender Insights", className="zone-title"), # Combined title
                    dcc.Graph(id='age-dist-graph-output', style={'height': '100%'}),    # Age chart
                ], md=5, className="zone-container", style={'height': '100%'}),# Third width
                dbc.Col([
                    html.Div([
                        html.P([
                            "Gender distribution."
                        ], className="text-muted mb-1")
                    ], className="px-2"),
                    dcc.Graph(id='gender-graph-output', style={'height': '100%'})
                ], md=3, className="zone-container", style={'height': '100%'}), # Third width
            ], style={'height': '28vh', 'marginBottom': '1vh'}),

            # --- Zone 3: Survival & Healthcare Impact ---
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.P([
                            "Family history can impact survival rates."
                        ], className="text-muted mb-1")
                    ], className="px-2"),
                    dcc.Graph(id='family-history-graph-output')
                ], md=4, className="zone-container"),
                dbc.Col([
                    html.Div([
                        html.P([
                            "Access to treatment has a strong impact on survival chances."
                        ], className="text-muted mb-1")
                    ], className="px-2"),
                    #html.H5("Treatment", className="zone-title"),
                    dcc.Graph(id='treatment-access-graph-output', style={'height': '100%'})
                ], md=4, className="zone-container", style={'height': '100%'}),
                dbc.Col([
                    html.Div([
                        html.P([
                            "Socioeconomic status affects cancer stage at diagnosis."
                        ], className="text-muted mb-1")
                    ], className="px-2"),
                    #html.H5("SES Impact", className="zone-title"),
                    dcc.Graph(id='ses-impact-graph-output', style={'height': '100%'})
                ], md=4, className="zone-container", style={'height': '100%'}),
            ], style={'height': '28vh'})
        ], width=12, lg=9, style={'height': '100%', 'overflowY': 'auto'})
    ], style={'height': '94vh'})
], fluid=True, style={'height': '100vh', 'overflowY': 'hidden', 'padding': '20px'})


def filter_data(df, continent='all', country='all', smoking='all', cancer_type='all', sex='all', age_range=(0,100), family_history='all', treatment_access = 'all', ses = 'all'):
    min_age, max_age = age_range
    filtered_df = df.copy()

    if continent != 'all':
        filtered_df = filtered_df[filtered_df['Continent'] == continent]
    if country != 'all':
        filtered_df = filtered_df[filtered_df['Country'] == country]
    if smoking != 'all':
        filtered_df = filtered_df[filtered_df['Smoking_Status'] == smoking]
    if cancer_type != 'all':
        filtered_df = filtered_df[filtered_df['Cancer_Type'] == cancer_type]
    if sex != 'all':
        filtered_df = filtered_df[filtered_df['Gender'] == sex]
    if family_history != 'all':
        filtered_df = filtered_df[filtered_df['Family_History'] == family_history]
    if treatment_access != 'all':
        filtered_df = filtered_df[filtered_df['Treatment_Access'] == treatment_access]
    if ses != 'all':
        filtered_df = filtered_df[filtered_df['Socioeconomic_Status'] == ses]
    filtered_df = filtered_df[
        (filtered_df['Age'] >= min_age) & (filtered_df['Age'] <= max_age)
        ]

    return filtered_df

@app.callback(
    [Output('map-graph-output', 'figure'),
     Output('smoking-risk-graph-output', 'figure'),
     Output('age-dist-graph-output', 'figure'),
     Output('gender-graph-output','figure'),
     Output('treatment-access-graph-output','figure'),
     Output('family-history-graph-output','figure'),
     Output('ses-impact-graph-output','figure'),
     Output('kpi-cards-output','children')],
    [Input('continent-filter', 'value'),
     Input('map-filter-country', 'data'),
     Input('smoking-filter', 'value'),
     Input('cancer-type-filter', 'value'),
     Input('sex-filter', 'value'),
     Input('age-range-slider', 'value'),
     Input('family-history-filter','value'),
     Input('treatment-access-filter','value'),
     Input('ses-filter', 'value')
     ]
)
def update_graphs(continent, selected_country_from_store, sidebar_smoking, cancer_type, sex, age_range, family_history, treatment_access,ses):
    filtered = filter_data(df.copy(), continent, selected_country_from_store, sidebar_smoking, cancer_type, sex, age_range, family_history, treatment_access, ses)
    fig_map = generate_geographic_map_figure(filtered)
    fig_smoking_risk = generate_smoking_risk_figure(filtered)
    fig_age_dist = generate_age_dist_figure(filtered)
    fig_gender_pie = generate_gender_pie_figure(filtered)
    fig_family_history = generate_family_history_impact_figure(filtered)
    fig_ses_impact = generate_ses_figure(filtered)
    fig_treatment_impact = generate_treatment_acces_figure(filtered)
    kpi_cards = generate_kpi_cards(filtered)
    return fig_map, fig_smoking_risk, fig_age_dist, fig_gender_pie, fig_treatment_impact, fig_family_history, fig_ses_impact, kpi_cards


@app.callback(
    Output('map-filter-country', 'data'),
    Output('selected-country-display', 'children'),
    Output('continent-filter', 'value', allow_duplicate=True),
    Input('map-graph-output', 'selectedData'),
    State('map-filter-country', 'data'),
    prevent_initial_call=True
)
def update_country_filter_from_map_selection(map_selected_data, current_country_in_store):

    # Default to no update unless a change is made
    new_country_for_store = dash.no_update
    new_country_display_text = dash.no_update
    new_continent_filter_value = dash.no_update

    if map_selected_data and map_selected_data['points']:
        selected_country_on_map = map_selected_data['points'][0]['hovertext']

        if selected_country_on_map != current_country_in_store: # Only update if different
            new_country_for_store = selected_country_on_map
            new_country_display_text = f"Selected: {selected_country_on_map}"
            new_continent_filter_value = country_to_continent.get(selected_country_on_map, 'all') # Default to 'all'
    else: # No points selected (e.g., selection cleared)
        if current_country_in_store != 'all':
            new_country_for_store = 'all'
            new_country_display_text = "All Countries"
            new_continent_filter_value = 'all'

    return new_country_for_store, new_country_display_text, new_continent_filter_value

@app.callback(
    Output('sex-filter', 'value'),
    Input('gender-graph-output', 'clickData'),
    State('sex-filter', 'value'),
    prevent_initial_call=True
)
def update_clicked_gender_radio_from_pie(clickData_pie, current_radio_value):
    if clickData_pie:
        clicked_gender_label = clickData_pie['points'][0]['label']
        if clicked_gender_label == current_radio_value:
            return 'all'
        else:
            return clicked_gender_label
    else:
        return dash.no_update

@app.callback(
    Output('smoking-filter', 'value'),
    Input('smoking-risk-graph-output', 'clickData'),
    State('smoking-filter', 'value')
)
def update_smoking_status_from_graph(clickData, current_radio_value):
    if clickData:
        clicked_smoked_label = clickData['points'][0]['x']
        if clicked_smoked_label == current_radio_value:
            return 'all'
        else:
            return clicked_smoked_label
    else:
        return dash.no_update


@app.callback(
    Output('family-history-filter','value'),
    Input('family-history-graph-output','clickData'),
    State('family-history-filter','value')
)
def update_family_history_from_graph(clickData, current_radio_value):
    if clickData:
        clicked_smoked_label = clickData['points'][0]['x']
        if clicked_smoked_label == current_radio_value:
            return 'all'
        else:
            return clicked_smoked_label
    else:
        return dash.no_update

@app.callback(
    Output('treatment-access-filter','value'),
    Input('treatment-access-graph-output','clickData'),
    State('treatment-access-filter','value')
)
def update_family_history_from_graph(clickData, current_radio_value):
    if clickData:
        clicked_smoked_label = clickData['points'][0]['x']
        if clicked_smoked_label == current_radio_value:
            return 'all'
        else:
            return clicked_smoked_label
    else:
        return dash.no_update

@app.callback(
    Output('ses-filter','value'),
    Input('ses-impact-graph-output','clickData'),
    State('ses-filter','value')
)
def update_family_history_from_graph(clickData, current_radio_value):
    if clickData:
        clicked_smoked_label = clickData['points'][0]['x']
        if clicked_smoked_label == current_radio_value:
            return 'all'
        else:
            return clicked_smoked_label
    else:
        return dash.no_update

@app.callback(
    [Output('continent-filter', 'value', allow_duplicate=True),
     Output('map-filter-country', 'data', allow_duplicate=True),
     Output('selected-country-display', 'children', allow_duplicate=True),
     Output('smoking-filter', 'value', allow_duplicate=True),
     Output('cancer-type-filter', 'value', allow_duplicate=True),
     Output('sex-filter', 'value', allow_duplicate=True),
     Output('age-range-slider', 'value'),
     Output('family-history-filter','value',allow_duplicate=True),
     Output('treatment-access-filter','value',allow_duplicate=True),
     Output('ses-filter','value',allow_duplicate=True)],
    Input('reset-filters-button', 'n_clicks'),
    prevent_initial_call=True
)
def reset_all_filters(n_clicks):
    return ('all', 'all', 'All Countries', 'all', 'all', 'all',
            [int(data['ages'].min()) if not data['ages'].empty else 0,
             int(data['ages'].max()) if not data['ages'].empty else 100],'all','all','all')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)