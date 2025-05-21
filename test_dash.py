from dash import Dash, dcc, html, Input, Output, State, callback_context
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

app = Dash(__name__)


# Load the real data
def load_real_data():
    # Load the real dataset
    df1 = pd.read_csv('lung_cancer_prediction.csv')

    # Convert smoking status to an ordered category
    smoking_order = ['Non-Smoker', 'Former Smoker', 'Smoker']
    df1['Smoking_Status'] = pd.Categorical(df1['Smoking_Status'], categories=smoking_order, ordered=True)

    # Convert categorical strings to categories if needed
    for col in ['Cancer_Type', 'Mutation_Type', 'Socioeconomic_Status', 'Treatment_Access']:
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
        'genders': df1['Gender'].unique().tolist()
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

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Lung Cancer Risk Analysis Dashboard",
                style={
                    'textAlign': 'center',
                    'fontSize': '28px',
                    'marginBottom': '20px',
                    'color': color_theme['text'],
                    'fontWeight': 'bold'
                })
    ], style={'backgroundColor': 'white', 'padding': '20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

    # Main Row: Sidebar + Content
    html.Div([
        # --- Sidebar Filters ---
        html.Div([
            html.H4("🔍 Filter Data",
                    style={'marginBottom': '20px', 'fontSize': '16px', 'color': color_theme['primary']}),

            html.Div([
                # Continent
                html.Div([
                    html.Label("🌍 Continent", style={'fontSize': '14px', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.RadioItems(
                        id='continent-filter',
                        options=[{'label': 'All', 'value': 'all'}] + [{'label': c, 'value': c} for c in
                                                                      data['continents']],
                        value='all',
                        labelStyle={
                            'display': 'block',
                            'padding': '5px 10px',
                            'margin': '3px 0',
                            'borderRadius': '4px',
                            'cursor': 'pointer',
                            'fontSize': '12px',
                            'transition': 'background-color 0.3s'
                        },
                        inputStyle={'marginRight': '8px'}
                    )
                ], style={'marginBottom': '10px'}),

                # Country (map)
                dcc.Store(id='map-filter', data='all'),

                # Smoking
                html.Div([
                    html.Label("🚬 Smoking Status",
                               style={'fontSize': '14px', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.RadioItems(
                        id='smoking-filter',
                        options=[
                            {'label': 'All', 'value': 'all'},
                            {'label': '🚭 Non-Smoker', 'value': 'Non-Smoker'},
                            {'label': '🫁 Former', 'value': 'Former Smoker'},
                            {'label': '🚬 Smoker', 'value': 'Smoker'}
                        ],
                        value='all',
                        labelStyle={
                            'display': 'block',
                            'padding': '5px 10px',
                            'margin': '3px 0',
                            'borderRadius': '4px',
                            'cursor': 'pointer',
                            'fontSize': '12px'
                        },
                        inputStyle={'marginRight': '8px'}
                    )
                ], style={'marginBottom': '10px'}),

                # Cancer Type
                html.Div([
                    html.Label("🔬 Cancer Type",
                               style={'fontSize': '14px', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.RadioItems(
                        id='cancer-type-filter',
                        options=[{'label': 'All', 'value': 'all'}] + [{'label': ct, 'value': ct} for ct in
                                                                      data['cancer_types']],
                        value='all',
                        labelStyle={
                            'display': 'block',
                            'padding': '5px 10px',
                            'margin': '3px 0',
                            'borderRadius': '4px',
                            'cursor': 'pointer',
                            'fontSize': '12px'
                        },
                        inputStyle={'marginRight': '8px'}
                    )
                ], style={'marginBottom': '10px'}),

                # Gender Filter
                html.Div([
                    html.Label("👥 Gender", style={'fontSize': '14px', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.RadioItems(
                        id='sex-filter',
                        options=[
                            {'label': 'All', 'value': 'all'},
                            {'label': '👩 Female', 'value': 'Female'},
                            {'label': '👨 Male', 'value': 'Male'}
                        ],
                        value='all',
                        labelStyle={
                            'display': 'block',
                            'padding': '5px 10px',
                            'margin': '3px 0',
                            'borderRadius': '4px',
                            'cursor': 'pointer',
                            'fontSize': '12px'
                        },
                        inputStyle={'marginRight': '8px'}
                    )
                ], style={'marginBottom': '10px'}),

                # Age Range
                html.Div([
                    html.Label("📊 Age Range", style={'fontSize': '14px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
                    dcc.RangeSlider(
                        id='age-range-slider',
                        min=int(df['Age'].min()),
                        max=int(df['Age'].max()),
                        value=[int(df['Age'].min()), int(df['Age'].max())],
                        marks={i: str(i) for i in range(int(df['Age'].min()), int(df['Age'].max()) + 1, 10)},
                        step=1,
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ], style={'marginBottom': '20px'})
            ], style={
                'padding': '20px',
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            }),

            # Personal Risk Calculator
            html.Div([
                html.H4("Personal Risk Assessment",
                        style={'marginTop': '20px', 'marginBottom': '15px', 'fontSize': '16px',
                               'color': color_theme['primary']}),

                html.Div([
                    # Age input
                    html.Div([
                        html.Label("Age:", style={'fontWeight': 'bold', 'fontSize': '14px'}),
                        dcc.Input(id='risk-age-input', type='number', min=1, max=100, value=50,
                                  style={'width': '100%', 'marginTop': '5px', 'padding': '5px'})
                    ], style={'marginBottom': '10px'}),

                    # Smoking status
                    html.Div([
                        html.Label("Smoking Status:", style={'fontWeight': 'bold', 'fontSize': '14px'}),
                        dcc.Dropdown(
                            id='risk-smoking-input',
                            options=[
                                {'label': 'Non-Smoker', 'value': 'Non-Smoker'},
                                {'label': 'Former Smoker', 'value': 'Former Smoker'},
                                {'label': 'Current Smoker', 'value': 'Smoker'}
                            ],
                            value='Non-Smoker',
                            style={'marginTop': '5px'}
                        )
                    ], style={'marginBottom': '10px'}),

                    # Air pollution exposure
                    html.Div([
                        html.Label("Air Pollution Exposure:", style={'fontWeight': 'bold', 'fontSize': '14px'}),
                        dcc.RadioItems(
                            id='risk-pollution-input',
                            options=[
                                {'label': 'Low', 'value': 'Low'},
                                {'label': 'Medium', 'value': 'Medium'},
                                {'label': 'High', 'value': 'High'}
                            ],
                            value='Low',
                            labelStyle={'marginRight': '10px', 'display': 'inline-block'}
                        )
                    ], style={'marginBottom': '10px'}),

                    # Family history
                    html.Div([
                        html.Label("Family History:", style={'fontWeight': 'bold', 'fontSize': '14px'}),
                        dcc.RadioItems(
                            id='risk-family-input',
                            options=[
                                {'label': 'No', 'value': 'No'},
                                {'label': 'Yes', 'value': 'Yes'}
                            ],
                            value='No',
                            labelStyle={'marginRight': '10px', 'display': 'inline-block'}
                        )
                    ], style={'marginBottom': '15px'}),

                    html.Button("Calculate My Risk", id='calculate-risk-btn',
                                style={'backgroundColor': color_theme['secondary'], 'color': 'white',
                                       'border': 'none', 'padding': '8px 15px', 'borderRadius': '4px',
                                       'cursor': 'pointer', 'width': '100%'})
                ], style={'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'}),

                # Result display area
                html.Div(id='risk-result', style={'marginTop': '10px'})
            ], style={'marginTop': '20px', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px',
                      'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ], style={
            'width': '280px',
            'marginRight': '20px',
            'flexShrink': 0
        }),

        # --- Main Content Area (All sections in one page) ---
        html.Div([
            html.Div(id='dashboard-content')
        ], style={'flex': 1})
    ], style={
        'display': 'flex',
        'padding': '20px',
        'backgroundColor': color_theme['background']
    })
])


# Callback to render all content
@app.callback(
    Output('dashboard-content', 'children'),
    [Input('continent-filter', 'value'),
     Input('map-filter', 'data'),
     Input('smoking-filter', 'value'),
     Input('cancer-type-filter', 'value'),
     Input('sex-filter', 'value'),
     Input('age-range-slider', 'value')]
)
def render_dashboard(continent, country, smoking, cancer_type, sex, age_range):
    filtered_df = filter_data(df, continent, country, smoking, cancer_type, sex, age_range)

    # Data summary statistics
    total_patients = len(filtered_df)
    avg_age = filtered_df['Age'].mean()
    avg_mortality = filtered_df['Mortality_Risk'].mean()
    avg_survival = filtered_df['5_Year_Survival_Probability'].mean()

    # Most common cancer type
    if not filtered_df.empty:
        most_common_cancer = filtered_df['Cancer_Type'].mode()[0]
    else:
        most_common_cancer = "No data"

    # Create the choropleth map figure
    choropleth_fig = px.choropleth(
        filtered_df.groupby('Country')['Mortality_Risk'].mean().reset_index(),
        locations="Country",
        locationmode="country names",
        color="Mortality_Risk",
        color_continuous_scale="Reds",
        title="Average Mortality Risk by Country",
        labels={"Mortality_Risk": "Mortality Risk"}
    )

    # Add id to the map graph for the clickData callback
    map_graph = dcc.Graph(
        id='choropleth-map',
        figure=choropleth_fig,
        config={'displayModeBar': True}
    )

    return html.Div([
        # Summary statistics
        html.Div([
            html.H3("Data Summary", style={'fontSize': '18px', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.Div([
                        html.H4(f"{total_patients:,}",
                                style={'margin': '0', 'textAlign': 'center', 'fontSize': '24px'}),
                        html.P("Total Patients", style={'margin': '5px 0 0 0', 'textAlign': 'center'})
                    ], style={'flex': '1', 'padding': '10px', 'backgroundColor': color_theme['primary'],
                              'color': 'white', 'borderRadius': '5px', 'margin': '0 5px'}),
                    html.Div([
                        html.H4(f"{avg_age:.1f}", style={'margin': '0', 'textAlign': 'center', 'fontSize': '24px'}),
                        html.P("Average Age", style={'margin': '5px 0 0 0', 'textAlign': 'center'})
                    ], style={'flex': '1', 'padding': '10px', 'backgroundColor': color_theme['secondary'],
                              'color': 'white', 'borderRadius': '5px', 'margin': '0 5px'}),
                    html.Div([
                        html.H4(f"{avg_survival:.1%}",
                                style={'margin': '0', 'textAlign': 'center', 'fontSize': '24px'}),
                        html.P("5-Year Survival", style={'margin': '5px 0 0 0', 'textAlign': 'center'})
                    ], style={'flex': '1', 'padding': '10px', 'backgroundColor': color_theme['tertiary'],
                              'color': 'white', 'borderRadius': '5px', 'margin': '0 5px'})
                ], style={'display': 'flex', 'marginBottom': '10px'}),
                html.Div([
                    html.P(f"Most common cancer type: {most_common_cancer}", style={'margin': '5px 0'})
                ])
            ], style={'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
        ], style={'marginBottom': '30px'}),

        # Geographic Section
        html.Div([
            html.H3("Geographic Distribution", style={'fontSize': '18px', 'marginBottom': '10px'}),
            html.Div([
                map_graph
            ])
        ], style={'marginBottom': '30px'}),

        # Risk Factors Section
        html.Div([
            html.H3("Risk Factors Analysis", style={'fontSize': '18px', 'marginBottom': '10px'}),
            html.Div([
                # Heat map of risk factors
                dcc.Graph(
                    figure=px.density_heatmap(
                        filtered_df,
                        x="Smoking_Status",
                        y="Air_Pollution_Exposure",
                        z="Mortality_Risk",
                        color_continuous_scale="Reds",
                        title="Mortality Risk by Smoking and Air Pollution"
                    )
                )
            ], style={'marginBottom': '20px'}),

            html.Div([
                # Bar chart of smoking status vs mortality
                dcc.Graph(
                    figure=px.bar(
                        filtered_df.groupby(['Smoking_Status'])['Mortality_Risk'].mean().reset_index(),
                        x='Smoking_Status',
                        y='Mortality_Risk',
                        color='Smoking_Status',
                        title="Average Mortality Risk by Smoking Status"
                    ).update_layout(xaxis_title="Smoking Status", yaxis_title="Mortality Risk")
                )
            ])
        ], style={'marginBottom': '30px'}),

        # Survival Analysis
        html.Div([
            html.H3("Survival Analysis", style={'fontSize': '18px', 'marginBottom': '10px'}),
            html.Div([
                # Survival by stage
                dcc.Graph(
                    figure=px.line(
                        filtered_df.groupby('Stage_at_Diagnosis')['5_Year_Survival_Probability'].mean().reset_index(),
                        x='Stage_at_Diagnosis',
                        y='5_Year_Survival_Probability',
                        markers=True,
                        title="5-Year Survival Probability by Cancer Stage",
                        labels={
                            "Stage_at_Diagnosis": "Stage at Diagnosis",
                            "5_Year_Survival_Probability": "5-Year Survival Probability"
                        }
                    ).update_layout(
                        xaxis={'categoryorder': 'array',
                               'categoryarray': ['Stage I', 'Stage II', 'Stage III', 'Stage IV']}
                    )
                )
            ], style={'marginBottom': '20px'}),

            html.Div([
                # Treatment vs survival
                dcc.Graph(
                    figure=px.bar(
                        filtered_df.groupby(['Treatment_Access', 'Stage_at_Diagnosis'])[
                            '5_Year_Survival_Probability'].mean().reset_index(),
                        x='Stage_at_Diagnosis',
                        y='5_Year_Survival_Probability',
                        color='Treatment_Access',
                        barmode='group',
                        title="Survival Probability by Stage and Treatment Access"
                    ).update_layout(
                        xaxis_title="Cancer Stage",
                        yaxis_title="5-Year Survival Probability",
                        xaxis={'categoryorder': 'array',
                               'categoryarray': ['Stage I', 'Stage II', 'Stage III', 'Stage IV']}
                    )
                )
            ])
        ])
    ])


def filter_data(df, continent, country, smoking, cancer_type, sex, age_range):
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

    filtered_df = filtered_df[
        (filtered_df['Age'] >= min_age) & (filtered_df['Age'] <= max_age)
        ]

    return filtered_df


@app.callback(
    Output('continent-filter', 'options'),
    Output('continent-filter', 'value'),
    Input('map-filter', 'data')
)
def update_continent_options(selected_country):
    # If 'All' is selected in country, show all continents options
    if selected_country == 'all':
        options = [{'label': 'All', 'value': 'all'}] + [{'label': c, 'value': c} for c in data['continents']]
        value = 'all'  # Reset continent selection
    else:
        # Get the continent(s) for the selected country
        continent = country_to_continent.get(selected_country, 'all')
        options = [{'label': continent, 'value': continent}]
        value = continent  # Set the continent to the selected one

    return options, value


# Fixed callback - using choropleth-map clickData instead of geographic-tab selectedData
@app.callback(
    Output('map-filter', 'data'),
    Input('choropleth-map', 'clickData')
)
def update_country_filter(click_data):
    if click_data and 'points' in click_data:
        selected_country = click_data['points'][0]['location']
        print(f"Selected country: {selected_country}")
        return selected_country
    return 'all'


# Callback for the risk calculator
@app.callback(
    Output('risk-result', 'children'),
    Input('calculate-risk-btn', 'n_clicks'),
    [State('risk-age-input', 'value'),
     State('risk-smoking-input', 'value'),
     State('risk-pollution-input', 'value'),
     State('risk-family-input', 'value')]
)
def calculate_risk(n_clicks, age, smoking, pollution, family):
    if n_clicks is None:
        return html.Div()

    # Calculate risk score based on factors
    risk_score = 0

    # Age factor
    if age <= 40:
        risk_score += 1
    elif age <= 60:
        risk_score += 2
    else:
        risk_score += 3

    # Smoking factor
    if smoking == 'Non-Smoker':
        risk_score += 1
    elif smoking == 'Former Smoker':
        risk_score += 2
    else:  # Current smoker
        risk_score += 4

    # Pollution factor
    if pollution == 'Low':
        risk_score += 1
    elif pollution == 'Medium':
        risk_score += 2
    else:  # High
        risk_score += 3

    # Family history
    if family == 'Yes':
        risk_score += 2

    # Normalize to 0-10 scale
    max_score = 12
    normalized_score = (risk_score / max_score) * 10

    # Determine risk level and advice
    if normalized_score < 3:
        risk_level = "Low"
        color = "green"
        advice = "Your risk is relatively low. Continue healthy habits and get regular check-ups."
    elif normalized_score < 6:
        risk_level = "Moderate"
        color = "orange"
        advice = "Your risk is moderate. Consider regular lung screenings and focus on reducing your exposure to risk factors."
    else:
        risk_level = "High"
        color = "red"
        advice = "Your risk is high. Consult with a healthcare provider about regular lung cancer screenings and ways to reduce your risk."

    # Create gauge chart for risk visualization
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=normalized_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Risk Score", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 3], 'color': 'green'},
                {'range': [3, 6], 'color': 'yellow'},
                {'range': [6, 10], 'color': 'red'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': normalized_score
            }
        }
    ))

    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    # Return the risk assessment
    return html.Div([
        html.H4(f"Risk Level: {risk_level}", style={'color': color, 'marginBottom': '10px', 'textAlign': 'center'}),
        dcc.Graph(figure=fig, config={'displayModeBar': False}),
        html.Div([
            html.H5("Recommendations:"),
            html.P(advice),
            html.Ul([
                html.Li("Avoid smoking and secondhand smoke"),
                html.Li("Limit exposure to air pollution and industrial chemicals"),
                html.Li("Maintain a healthy diet and exercise regularly"),
                html.Li("Discuss screening options with your doctor")
            ])
        ], style={'marginTop': '15px', 'backgroundColor': '#f8f9fa', 'padding': '10px', 'borderRadius': '5px'})
    ])


# Run the app
if __name__ == '__main__':
    app.run(debug=True)