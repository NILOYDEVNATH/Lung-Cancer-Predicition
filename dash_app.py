import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Assume df is your cancer dataset
df = pd.read_csv('lung_cancer_prediction.csv')

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

colors = {
    'background': '#f9f9f9',
    'text': '#333333',
    'primary': '#007bff',
    'secondary': '#6c757d',
    'success': '#28a745',
    'danger': '#dc3545'
}

# App layout
app.layout = dbc.Container([
    html.Div([
        dbc.Row([
            dbc.Col([
                html.H4("Filters", style={'color': colors['primary']}),

                html.Label("Countries:"),
                dcc.Dropdown(
                    id='country-filter',
                    options=[{'label': country, 'value': country} for country in
                             sorted(df['Country'].unique())],
                    multi=True,
                    value=[],
                    placeholder="Select countries (all if empty)"
                ),

                html.Label("Age Range:", style={'marginTop': 15}),
                dcc.RangeSlider(
                    id='age-filter',
                    min=int(df['Age'].min()),
                    max=int(df['Age'].max()),
                    value=[int(df['Age'].min()), int(df['Age'].max())],
                    marks={i: str(i) for i in
                           range(int(df['Age'].min()), int(df['Age'].max()) + 1, 10)},
                    step=1
                ),

                html.Label("Gender:", style={'marginTop': 15}),
                dcc.Checklist(
                    id='gender-filter',
                    options=[{'label': gender, 'value': gender} for gender in df['Gender'].unique()],
                    value=df['Gender'].unique().tolist(),
                    inline=True
                ),

                html.Label("Smoking Status:", style={'marginTop': 15}),
                dcc.Checklist(
                    id='smoking-filter',
                    options=[{'label': status, 'value': status} for status in
                             df['Smoking_Status'].unique()],
                    value=df['Smoking_Status'].unique().tolist(),
                    inline=True
                ),

                html.Label("Stage at Diagnosis:", style={'marginTop': 15}),
                dcc.Checklist(
                    id='stage-filter',
                    options=[{'label': stage, 'value': stage} for stage in
                             sorted(df['Stage_at_Diagnosis'].unique())],
                    value=df['Stage_at_Diagnosis'].unique().tolist(),
                    inline=True
                ),

                html.Button('Apply Filters', id='apply-filters', n_clicks=0,
                            style={'marginTop': 20, 'backgroundColor': colors['primary'], 'color': 'white',
                                   'border': 'none', 'padding': '10px 15px', 'borderRadius': '5px'})
            ], width=3, style={'backgroundColor': '#f0f0f0', 'padding': '20px', 'borderRadius': '10px'}),

            dbc.Col([
                dbc.Tabs([
                    dbc.Tab(label="Risk Factors", children=[
                        dbc.Row([
                            dbc.Col([
                                html.H5("Risk Distribution", style={'textAlign': 'center', 'marginTop': 15}),
                                dcc.Graph(id='risk-factors-graph')
                            ], width=6),
                            dbc.Col([
                                html.H5("Smoking & Environmental Impact",
                                        style={'textAlign': 'center', 'marginTop': 15}),
                                dcc.Graph(id='smoking-environment-graph')
                            ], width=6)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5("Age & Gender Distribution", style={'textAlign': 'center', 'marginTop': 15}),
                                dcc.Graph(id='demographics-graph')
                            ], width=12)
                        ])
                    ]),

                    dbc.Tab(label="Diagnosis & Treatment", children=[
                        dbc.Row([
                            dbc.Col([
                                html.H5("Stage Distribution", style={'textAlign': 'center', 'marginTop': 15}),
                                dcc.Graph(id='stage-distribution-graph')
                            ], width=6),
                            dbc.Col([
                                html.H5("Treatment Access by Socioeconomic Factors",
                                        style={'textAlign': 'center', 'marginTop': 15}),
                                dcc.Graph(id='treatment-access-graph')
                            ], width=6)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5("Diagnosis Delay Factors", style={'textAlign': 'center', 'marginTop': 15}),
                                dcc.Graph(id='diagnosis-delay-graph')
                            ], width=12)
                        ])
                    ]),

                    dbc.Tab(label="Survival & Outcomes", children=[
                        dbc.Row([
                            dbc.Col([
                                html.H5("Survival by Stage & Age", style={'textAlign': 'center', 'marginTop': 15}),
                                dcc.Graph(id='survival-stage-graph')
                            ], width=6),
                            dbc.Col([
                                html.H5("Mortality Risk Factors", style={'textAlign': 'center', 'marginTop': 15}),
                                dcc.Graph(id='mortality-factors-graph')
                            ], width=6)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5("Survival Probability by Country & Healthcare Access",
                                        style={'textAlign': 'center', 'marginTop': 15}),
                                dcc.Graph(id='country-survival-graph')
                            ], width=12)
                        ])
                    ]),

                    dbc.Tab(label="Geographic Analysis", children=[
                        dbc.Row([
                            dbc.Col([
                                html.H5("Lung Cancer Patterns by Country",
                                        style={'textAlign': 'center', 'marginTop': 15}),
                                dcc.Graph(id='geographic-distribution-graph')
                            ], width=12)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5("Urban vs Rural Comparison", style={'textAlign': 'center', 'marginTop': 15}),
                                dcc.Graph(id='urban-rural-graph')
                            ], width=12)
                        ])
                    ])
                ])
            ], width=9)
        ]),
    ], style={'padding': '20px', 'backgroundColor': colors['background']})
], fluid=True)


# Filter data based on user selections
def filter_data(countries, age_range, genders, smoking_statuses, stages):
    filtered_df = df.copy()

    if countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(countries)]

    filtered_df = filtered_df[
        (filtered_df['Age'] >= age_range[0]) &
        (filtered_df['Age'] <= age_range[1]) &
        (filtered_df['Gender'].isin(genders)) &
        (filtered_df['Smoking_Status'].isin(smoking_statuses)) &
        (filtered_df['Stage_at_Diagnosis'].isin(stages))
        ]

    return filtered_df

# Callbacks for interactivity
@app.callback(
    Output('risk-factors-graph', 'figure'),
    [Input('apply-filters', 'n_clicks')],
    [State('country-filter', 'value'),
     State('age-filter', 'value'),
     State('gender-filter', 'value'),
     State('smoking-filter', 'value'),
     State('stage-filter', 'value')]
)
def update_risk_factors(n_clicks, countries, age_range, genders, smoking_statuses, stages):
    filtered_df = filter_data(countries, age_range, genders, smoking_statuses, stages)

    risk_factors = ['Smoking_Status', 'Second_Hand_Smoke', 'Air_Pollution_Exposure',
                    'Occupation_Exposure', 'Indoor_Smoke_Exposure']

    df_melted = pd.melt(filtered_df,
                        id_vars=['Country', 'Age', 'Gender'],
                        value_vars=risk_factors,
                        var_name='Risk Factor',
                        value_name='Value')

    # For categorical variables like smoking status, convert to numeric for visualization
    smoking_map = {'Current Smoker': 10, 'Former Smoker': 5, 'Never Smoker': 0}
    df_melted.loc[df_melted['Risk Factor'] == 'Smoking_Status', 'Value'] = \
        df_melted.loc[df_melted['Risk Factor'] == 'Smoking_Status', 'Value'].map(smoking_map)

    fig = px.box(df_melted,
                 x='Risk Factor',
                 y='Value',
                 color='Gender',
                 title='Distribution of Lung Cancer Risk Factors',
                 labels={'Value': 'Exposure Level (0-10)'},
                 category_orders={"Risk Factor": risk_factors})

    fig.update_layout(
        plot_bgcolor='white',
        legend_title_text='Gender',
        boxmode='group'
    )

    return fig


# Smoking & Environment Graph
@app.callback(
    Output('smoking-environment-graph', 'figure'),
    [Input('apply-filters', 'n_clicks')],
    [State('country-filter', 'value'),
     State('age-filter', 'value'),
     State('gender-filter', 'value'),
     State('smoking-filter', 'value'),
     State('stage-filter', 'value')]
)
def update_smoking_environment(n_clicks, countries, age_range, genders, smoking_statuses, stages):
    filtered_df = filter_data(countries, age_range, genders, smoking_statuses, stages)

    # Create a scatter plot with size indicating mortality risk
    fig = px.scatter(filtered_df,
                     x='Air_Pollution_Exposure',
                     y='Indoor_Smoke_Exposure',
                     size='Mortality_Risk',
                     color='Smoking_Status',
                     hover_data=['Age', 'Gender', 'Country'],
                     title='Relationship Between Environmental Factors and Mortality',
                     labels={'Air_Pollution_Exposure': 'Air Pollution Exposure (0-10)',
                             'Indoor_Smoke_Exposure': 'Indoor Smoke Exposure (0-10)'})

    fig.update_layout(
        plot_bgcolor='white',
        legend_title_text='Smoking Status'
    )

    return fig


# Demographics Graph
@app.callback(
    Output('demographics-graph', 'figure'),
    [Input('apply-filters', 'n_clicks')],
    [State('country-filter', 'value'),
     State('age-filter', 'value'),
     State('gender-filter', 'value'),
     State('smoking-filter', 'value'),
     State('stage-filter', 'value')]
)
def update_demographics(n_clicks, countries, age_range, genders, smoking_statuses, stages):
    filtered_df = filter_data(countries, age_range, genders, smoking_statuses, stages)

    fig = px.histogram(filtered_df,
                       x='Age',
                       color='Gender',
                       facet_col='Smoking_Status',
                       title='Age Distribution by Gender and Smoking Status',
                       labels={'Age': 'Age (years)'},
                       opacity=0.7)

    fig.update_layout(
        plot_bgcolor='white',
        bargap=0.1
    )

    return fig


# Stage Distribution Graph
@app.callback(
    Output('stage-distribution-graph', 'figure'),
    [Input('apply-filters', 'n_clicks')],
    [State('country-filter', 'value'),
     State('age-filter', 'value'),
     State('gender-filter', 'value'),
     State('smoking-filter', 'value'),
     State('stage-filter', 'value')]
)
def update_stage_distribution(n_clicks, countries, age_range, genders, smoking_statuses, stages):
    filtered_df = filter_data(countries, age_range, genders, smoking_statuses, stages)

    # Order stages properly for visualization
    stage_order = ['Stage I', 'Stage II', 'Stage III', 'Stage IV']

    # Get counts for each stage by smoking status
    stage_counts = filtered_df.groupby(['Smoking_Status', 'Stage_at_Diagnosis']).size().reset_index(name='Count')

    fig = px.bar(stage_counts,
                 x='Stage_at_Diagnosis',
                 y='Count',
                 color='Smoking_Status',
                 barmode='group',
                 title='Cancer Stage Distribution by Smoking Status',
                 category_orders={"Stage_at_Diagnosis": stage_order})

    fig.update_layout(
        plot_bgcolor='white',
        xaxis_title='Stage at Diagnosis',
        yaxis_title='Number of Patients'
    )

    return fig


@app.callback(
    Output('treatment-access-graph', 'figure'),
    [Input('apply-filters', 'n_clicks')],
    [State('country-filter', 'value'),
     State('age-filter', 'value'),
     State('gender-filter', 'value'),
     State('smoking-filter', 'value'),
     State('stage-filter', 'value')]
)
def update_treatment_access(n_clicks, countries, age_range, genders, smoking_statuses, stages):
    filtered_df = filter_data(countries, age_range, genders, smoking_statuses, stages)

    fig = px.box(filtered_df,
                 x='Socioeconomic_Status',
                 y='Treatment_Access',
                 color='Insurance_Coverage',
                 title='Treatment Access by Socioeconomic Status and Insurance',
                 labels={'Treatment_Access': 'Treatment Access Score (0-10)',
                         'Socioeconomic_Status': 'Socioeconomic Status'},
                 category_orders={"Socioeconomic_Status": ['Low', 'Medium', 'High'],
                                  "Insurance_Coverage": ['None', 'Basic', 'Comprehensive']})

    fig.update_layout(
        plot_bgcolor='white',
        legend_title_text='Insurance Coverage'
    )

    return fig


# Diagnosis Delay Graph
@app.callback(
    Output('diagnosis-delay-graph', 'figure'),
    [Input('apply-filters', 'n_clicks')],
    [State('country-filter', 'value'),
     State('age-filter', 'value'),
     State('gender-filter', 'value'),
     State('smoking-filter', 'value'),
     State('stage-filter', 'value')]
)
def update_diagnosis_delay(n_clicks, countries, age_range, genders, smoking_statuses, stages):
    filtered_df = filter_data(countries, age_range, genders, smoking_statuses, stages)

    # Create scatter plot with healthcare access vs delay in diagnosis
    fig = px.scatter(filtered_df,
                     x='Healthcare_Access',
                     y='Delay_in_Diagnosis',
                     color='Rural_or_Urban',
                     size='Age',
                     facet_col='Socioeconomic_Status',
                     title='Factors Affecting Delay in Diagnosis',
                     labels={'Delay_in_Diagnosis': 'Delay in Diagnosis (months)',
                             'Healthcare_Access': 'Healthcare Access'})

    fig.update_layout(
        plot_bgcolor='white',
        height=500
    )

    return fig


# Survival by Stage Graph
@app.callback(
    Output('survival-stage-graph', 'figure'),
    [Input('apply-filters', 'n_clicks')],
    [State('country-filter', 'value'),
     State('age-filter', 'value'),
     State('gender-filter', 'value'),
     State('smoking-filter', 'value'),
     State('stage-filter', 'value')]
)
def update_survival_stage(n_clicks, countries, age_range, genders, smoking_statuses, stages):
    filtered_df = filter_data(countries, age_range, genders, smoking_statuses, stages)

    # Create scatter plot of age vs survival probability colored by stage
    fig = px.scatter(filtered_df,
                     x='Age',
                     y='5_Year_Survival_Probability',
                     color='Stage_at_Diagnosis',
                     title='5-Year Survival Probability by Age and Cancer Stage',
                     labels={'5_Year_Survival_Probability': 'Survival Probability',
                             'Age': 'Age (years)'},
                     category_orders={"Stage_at_Diagnosis": ['Stage I', 'Stage II', 'Stage III', 'Stage IV']})

    # Add trendlines
    fig = px.scatter(filtered_df,
                     x='Age',
                     y='5_Year_Survival_Probability',
                     color='Stage_at_Diagnosis',
                     trendline="lowess",
                     title='5-Year Survival Probability by Age and Cancer Stage',
                     labels={'5_Year_Survival_Probability': 'Survival Probability',
                             'Age': 'Age (years)'},
                     category_orders={"Stage_at_Diagnosis": ['Stage I', 'Stage II', 'Stage III', 'Stage IV']})

    fig.update_layout(
        plot_bgcolor='white',
        legend_title_text='Stage at Diagnosis'
    )

    return fig


# Mortality Factors Graph
@app.callback(
    Output('mortality-factors-graph', 'figure'),
    [Input('apply-filters', 'n_clicks')],
    [State('country-filter', 'value'),
     State('age-filter', 'value'),
     State('gender-filter', 'value'),
     State('smoking-filter', 'value'),
     State('stage-filter', 'value')]
)
def update_mortality_factors(n_clicks, countries, age_range, genders, smoking_statuses, stages):
    filtered_df = filter_data(countries, age_range, genders, smoking_statuses, stages)

    # Create heatmap of mortality risk based on treatment access and clinical trial access
    heatmap_data = filtered_df.pivot_table(
        values='Mortality_Risk',
        index='Treatment_Access',
        columns='Clinical_Trial_Access',
        aggfunc='mean'
    ).round(2)

    # Convert to integers for cleaner visualization if needed
    heatmap_data.index = heatmap_data.index.astype(int)
    heatmap_data.columns = heatmap_data.columns.astype(int)

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Reds',
        hoverongaps=False))

    fig.update_layout(
        title='Mortality Risk by Treatment and Clinical Trial Access',
        xaxis_title='Clinical Trial Access Score',
        yaxis_title='Treatment Access Score',
        plot_bgcolor='white'
    )

    return fig


# Country Survival Graph
@app.callback(
    Output('country-survival-graph', 'figure'),
    [Input('apply-filters', 'n_clicks')],
    [State('country-filter', 'value'),
     State('age-filter', 'value'),
     State('gender-filter', 'value'),
     State('smoking-filter', 'value'),
     State('stage-filter', 'value')]
)
def update_country_survival(n_clicks, countries, age_range, genders, smoking_statuses, stages):
    filtered_df = filter_data(countries, age_range, genders, smoking_statuses, stages)

    # Get average survival by country and healthcare access
    survival_by_country = filtered_df.groupby(['Country', 'Healthcare_Access'])[
        '5_Year_Survival_Probability'].mean().reset_index()

    fig = px.bar(survival_by_country,
                 x='Country',
                 y='5_Year_Survival_Probability',
                 color='Healthcare_Access',
                 title='Average 5-Year Survival Probability by Country and Healthcare Access',
                 labels={'5_Year_Survival_Probability': 'Avg. Survival Probability',
                         'Country': 'Country'},
                 category_orders={"Healthcare_Access": ['Limited', 'Moderate', 'Good', 'Excellent']})

    fig.update_layout(
        plot_bgcolor='white',
        legend_title_text='Healthcare Access'
    )

    return fig


# Geographic Distribution Graph
@app.callback(
    Output('geographic-distribution-graph', 'figure'),
    [Input('apply-filters', 'n_clicks')],
    [State('country-filter', 'value'),
     State('age-filter', 'value'),
     State('gender-filter', 'value'),
     State('smoking-filter', 'value'),
     State('stage-filter', 'value')]
)
def update_geographic_distribution(n_clicks, countries, age_range, genders, smoking_statuses, stages):
    filtered_df = filter_data(countries, age_range, genders, smoking_statuses, stages)

    # Get statistics by country
    country_stats = filtered_df.groupby('Country').agg({
        'Mortality_Risk': 'mean',
        '5_Year_Survival_Probability': 'mean',
        'Age': 'mean',
        'Treatment_Access': 'mean'
    }).reset_index()

    fig = px.scatter_geo(country_stats,
                         locations='Country',
                         locationmode='country names',
                         size='Mortality_Risk',
                         color='5_Year_Survival_Probability',
                         hover_data=['Age', 'Treatment_Access'],
                         projection='natural earth',
                         title='Lung Cancer Patterns by Country',
                         color_continuous_scale=px.colors.sequential.Viridis_r)

    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            showocean=True,
            oceancolor='rgb(230, 245, 255)'
        )
    )

    return fig


# Urban Rural Graph
@app.callback(
    Output('urban-rural-graph', 'figure'),
    [Input('apply-filters', 'n_clicks')],
    [State('country-filter', 'value'),
     State('age-filter', 'value'),
     State('gender-filter', 'value'),
     State('smoking-filter', 'value'),
     State('stage-filter', 'value')]
)
def update_urban_rural(n_clicks, countries, age_range, genders, smoking_statuses, stages):
    filtered_df = filter_data(countries, age_range, genders, smoking_statuses, stages)

    # Create parallel coordinates plot for urban vs rural comparison
    dimensions = ['Healthcare_Access', 'Treatment_Access', 'Clinical_Trial_Access',
                  'Delay_in_Diagnosis', '5_Year_Survival_Probability']

    # Convert categorical healthcare access to numeric for parallel coordinates
    healthcare_map = {'Limited': 0, 'Moderate': 1, 'Good': 2, 'Excellent': 3}
    parallel_df = filtered_df.copy()
    parallel_df['Healthcare_Access'] = parallel_df['Healthcare_Access'].map(healthcare_map)

    fig = px.parallel_coordinates(parallel_df,
                                  dimensions=dimensions,
                                  color='Rural_or_Urban',
                                  title='Urban vs Rural: Healthcare and Outcome Comparison',
                                  labels={
                                      'Healthcare_Access': 'Healthcare Access',
                                      'Treatment_Access': 'Treatment Access',
                                      'Clinical_Trial_Access': 'Clinical Trial Access',
                                      'Delay_in_Diagnosis': 'Diagnosis Delay (months)',
                                      '5_Year_Survival_Probability': 'Survival Probability'
                                  },
                                  color_continuous_scale=px.colors.diverging.Tealrose)

    fig.update_layout(
        plot_bgcolor='white'
    )

    return fig






# Run the app
if __name__ == '__main__':
    app.run(debug=True)