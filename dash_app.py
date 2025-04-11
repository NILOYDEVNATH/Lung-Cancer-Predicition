from dash import Dash, dcc, html, Input, Output, State, callback_context
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from flask_caching import Cache

# Initialize the app
app = Dash(__name__)
cache = Cache(app.server, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300  # in seconds
})


# Load the real data
@cache.memoize()
def load_real_data():
    # Load the real dataset
    df = pd.read_csv('lung_cancer_prediction.csv')

    # Convert smoking status to an ordered category
    smoking_order = ['Non-Smoker', 'Former Smoker', 'Smoker']
    df['Smoking_Status'] = pd.Categorical(df['Smoking_Status'], categories=smoking_order, ordered=True)

    # Convert categorical strings to categorize if needed
    for col in ['Cancer_Type', 'Mutation_Type', 'Socioeconomic_Status', 'Treatment_Access']:
        if df[col].dtype == 'object':
            df[col] = df[col].astype('category')

    # Return the dataframe and other processed data
    return {
        'dataframe': df,
        'countries': df['Country'].unique().tolist(),
        'continents': df['Continent'].unique().tolist(),
        'smoking_status': smoking_order,
        'cancer_types': df['Cancer_Type'].unique().tolist(),
        'mutation_types': [mt for mt in df['Mutation_Type'].unique() if pd.notna(mt)],
        'ages': df['Age'],
        'genders': df['Gender'].unique().tolist()
    }


# Get the real data
data = load_real_data()
df = data['dataframe']

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        # html.H1("Lung Cancer Risk Analysis Dashboard", style={'textAlign': 'center'}),

        # Navigation Tabs
        dcc.Tabs(id='tabs', value='demographics', children=[
            # dcc.Tab(label='Demographics', value='demographics'),
            # dcc.Tab(label='Risk Factors', value='risk_factors'),
            # dcc.Tab(label='Geographic Analysis', value='geographic'),
            # dcc.Tab(label='Healthcare Impact', value='healthcare'),
            # dcc.Tab(label='Survival Analysis', value='survival'),
        ]),
    ]),

    # Content
    html.Div(id='tabs-content')
])


# Callback to render the selected tab content
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):
    # if tab == 'demographics':
        df['AgeGroup'] = pd.cut(df['Age'], bins=10).astype(str)
        df['Mortality_Risk_Bin'] = pd.cut(df['Mortality_Risk'], bins=10).astype(str)
        df['Survival_Bin'] = pd.cut(df['5_Year_Survival_Probability'], bins=10).astype(str)
        return html.Div([
            html.Div([

                # World map with circles
                html.Div([
                    dcc.Graph(id='geographic-map')
                ], style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'top'}),

                # Filters
                html.Div([
                    html.H3("Filter Controls"),

                    html.Label("Filter by Continent:"),
                    dcc.Dropdown(
                        id='continent-filter',
                        options=[{'label': 'All', 'value': 'all'}] +
                                [{'label': c, 'value': c} for c in data['continents']],
                        value='all'
                    ),

                    html.Label("Filter by Smoking Status:"),
                    dcc.Dropdown(
                        id='smoking-filter',
                        options=[
                            {'label': 'All', 'value': 'all'},
                            {'label': 'Non-Smoker', 'value': 'Non-Smoker'},
                            {'label': 'Former Smoker', 'value': 'Former Smoker'},
                            {'label': 'Smoker', 'value': 'Smoker'}
                        ],
                        value='all'
                    ),

                    html.Label("Filter by Cancer Type:"),
                    dcc.Dropdown(
                        id='cancer-type-filter',
                        options=[{'label': 'All', 'value': 'all'}] +
                                [{'label': ct, 'value': ct} for ct in data['cancer_types']],
                        value='all'
                    ),

                    html.Label("Minimum Age:"),
                    dcc.Slider(
                        id='min-age-slider',
                        min=int(df['Age'].min()),
                        max=int(df['Age'].max()),
                        value=int(df['Age'].min()),
                        marks={i: str(i) for i in range(int(df['Age'].min()), int(df['Age'].max()) + 1, 10)},
                        step=5
                    ),

                    html.Button('Apply Filters', id='apply-filters-button', n_clicks=0),
                ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '20px'}),

                # Age Distribution
                html.Div([
                    dcc.Graph(
                        figure=px.histogram(
                            df,
                            x="AgeGroup",
                            color="AgeGroup",
                            title="Age Distribution",
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        ).update_layout(showlegend=False, xaxis_title="Age Range")
                    )
                ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

                # Gender Breakdown
                html.Div([
                    dcc.Graph(
                        figure=px.pie(
                            df.groupby('Gender').size().reset_index(name='Count'),
                            values='Count',
                            names='Gender',
                            title="Gender Distribution",
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                    )
                ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

                # World Map - Case Distribution by Continent
                html.Div([
                    dcc.Graph(
                        figure=px.bar(
                            df.groupby('Continent').size().reset_index(name='Count'),
                            x='Continent',
                            y='Count',
                            title="Lung Cancer Cases by Continent",
                            color='Count',
                            color_continuous_scale='Reds'
                        )
                    )
                ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),
            ]),

            # Second row - Additional demographics
            html.Div([
                # Cancer Type Breakdown
                html.Div([
                    dcc.Graph(
                        figure=px.bar(
                            df.groupby('Cancer_Type').size().reset_index(name='Count'),
                            x='Cancer_Type',
                            y='Count',
                            color='Cancer_Type',
                            title="Distribution by Cancer Type",
                            color_discrete_sequence=px.colors.qualitative.Bold
                        )
                    )
                ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),

                # Mutation Type Breakdown
                html.Div([
                    dcc.Graph(
                        figure=px.bar(
                            df[df['Mutation_Type'].notna()].groupby('Mutation_Type').size().reset_index(name='Count'),
                            x='Mutation_Type',
                            y='Count',
                            color='Mutation_Type',
                            title="Distribution by Mutation Type",
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                    )
                ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),

                # Main Risk Heatmap
                html.Div([
                    # Air Pollution
                    dcc.Graph(
                        figure=px.box(
                            df,
                            x='Air_Pollution_Exposure',
                            y='Mortality_Risk',
                            title="Mortality Risk by Air Pollution Level",
                            color='Air_Pollution_Exposure',
                            category_orders={"Air_Pollution_Exposure": ['Low', 'Medium', 'High']}
                        )
                    ),
                ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),

                # Risk Factor Bar Charts
                html.Div([
                    # Smoking Status
                    dcc.Graph(
                        figure=px.box(
                            df,
                            x='Smoking_Status',
                            y='Mortality_Risk',
                            title="Mortality Risk by Smoking Status",
                            color='Smoking_Status',
                            category_orders={"Smoking_Status": ['Non-Smoker', 'Former Smoker', 'Smoker']}
                        )
                    ),
                ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
            ]),
            html.Div([
                # SES vs. Cancer Stage
                html.Div([
                    dcc.Graph(
                        figure=px.histogram(
                            df,
                            x="Socioeconomic_Status",
                            color="Stage_at_Diagnosis",
                            barmode='group',
                            title="Cancer Stage by Socioeconomic Status",
                            category_orders={"Socioeconomic_Status": ["Low", "Middle", "High"]},
                            color_discrete_sequence=px.colors.qualitative.Set2
                        )
                    )
                ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

                # Screening vs. Stage at Diagnosis
                html.Div([
                    dcc.Graph(
                        figure=px.histogram(
                            df,
                            x="Screening_Availability",
                            color="Stage_at_Diagnosis",
                            barmode='group',
                            title="Stage at Diagnosis by Screening Availability",
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                    )
                ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

                # Treatment Access vs. Survival
                html.Div([
                    dcc.Graph(
                        figure=px.box(
                            df,
                            x="Treatment_Access",
                            y="5_Year_Survival_Probability",
                            color="Treatment_Access",
                            title="5-Year Survival Probability by Treatment Access",
                            category_orders={"Treatment_Access": ["None", "Partial", "Full"]},
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                    )
                ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'})
            ]),
            html.Div([
                # Healthcare Access
                html.Div([
                    dcc.Graph(
                        figure=px.box(
                            df,
                            x="Healthcare_Access",
                            y="5_Year_Survival_Probability",
                            color="Healthcare_Access",
                            title="Survival Probability by Healthcare Access",
                            category_orders={"Healthcare_Access": ["Poor", "Limited", "Good"]},
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                    )
                ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),

                # Insurance Coverage
                html.Div([
                    dcc.Graph(
                        figure=px.violin(
                            df,
                            x="Insurance_Coverage",
                            y="5_Year_Survival_Probability",
                            color="Insurance_Coverage",
                            box=True,
                            title="Survival Probability by Insurance Coverage",
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                    )
                ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'})
            ]),
            html.Div([
                # Distribution of Mortality Risk
                html.Div([
                    dcc.Graph(
                        figure=px.histogram(
                            df,
                            x='Mortality_Risk_Bin',
                            color='Mortality_Risk_Bin',
                            title="Mortality Risk Distribution",
                            color_discrete_sequence=px.colors.sequential.Oranges
                        ).update_layout(
                            xaxis_title="Mortality Risk",
                            yaxis_title="Number of Patients",
                            bargap=0.1,
                        )
                    )
                ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

                # Distribution of 5-Year Survival
                html.Div([
                    dcc.Graph(
                        figure=px.histogram(
                            df,
                            x="5_Year_Survival_Probability",
                            color="Survival_Bin",  # multiple colors based on bins
                            title="Distribution of 5-Year Survival Probability",
                            color_discrete_sequence=px.colors.qualitative.Set3
                        ).update_layout(
                            xaxis_title="5-Year Survival Probability",
                            yaxis_title="Number of Patients",
                            bargap=0.2,
                        )
                    )
                ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

                # Family History Impact
                html.Div([
                    dcc.Graph(
                        figure=px.box(
                            df,
                            x="Family_History",
                            y="5_Year_Survival_Probability",
                            color="Family_History",
                            title="Impact of Family History on Survival Probability",
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                    )
                ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'})
            ]),
            html.Div([
                # Cancer Type vs Survival
                html.Div([
                    dcc.Graph(
                        figure=px.box(
                            df,
                            x="Cancer_Type",
                            y="5_Year_Survival_Probability",
                            color="Cancer_Type",
                            title="Survival Probability by Cancer Type",
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                    )
                ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),

                # Mutation Type vs Survival
                html.Div([
                    dcc.Graph(
                        figure=px.box(
                            df[df['Mutation_Type'].notna()],
                            x="Mutation_Type",
                            y="5_Year_Survival_Probability",
                            color="Mutation_Type",
                            title="Survival Probability by Mutation Type",
                            color_discrete_sequence=px.colors.qualitative.Safe
                        )
                    )
                ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'})
            ])
        ])

# Callback for risk factors interaction plot
@app.callback(
    Output('risk-interaction-plot', 'figure'),
    [Input('factor1-dropdown', 'value'),
     Input('factor2-dropdown', 'value')]
)
def update_risk_interaction(factor1, factor2):
    # Group by the two factors and calculate mean mortality risk
    grouped = df.groupby([factor1, factor2])['Mortality_Risk'].mean().reset_index()

    # Create a different plot type based on the factor types
    if len(df[factor1].unique()) <= 5 and len(df[factor2].unique()) <= 5:
        # Both factors have few categories - use heatmap
        pivot_table = grouped.pivot_table(values='Mortality_Risk', index=factor1, columns=factor2)
        fig = px.imshow(
            pivot_table,
            labels=dict(x=factor2.replace('_', ' '), y=factor1.replace('_', ' '), color="Avg Mortality Risk"),
            title=f"Mortality Risk: {factor1.replace('_', ' ')} vs {factor2.replace('_', ' ')}",
            color_continuous_scale="Reds"
        )
    else:
        # Too many categories for a clean heatmap - use scatter plot
        fig = px.scatter(
            grouped,
            x=factor1,
            y=factor2,
            size='Mortality_Risk',
            color='Mortality_Risk',
            hover_name=factor1,
            size_max=30,
            title=f"Mortality Risk: {factor1.replace('_', ' ')} vs {factor2.replace('_', ' ')}",
            color_continuous_scale="Reds"
        )

    return fig


# Callback for geographic map
@app.callback(
    Output('geographic-map', 'figure'),
    [Input('apply-filters-button', 'n_clicks')],
    [State('continent-filter', 'value'),
     State('smoking-filter', 'value'),
     State('cancer-type-filter', 'value'),
     State('min-age-slider', 'value')]
)
def update_geographic_map(n_clicks, continent, smoking, cancer_type, min_age):
    # Apply filters
    filtered_df = df.copy()

    if continent != 'all':
        filtered_df = filtered_df[filtered_df['Continent'] == continent]

    if smoking != 'all':
        filtered_df = filtered_df[filtered_df['Smoking_Status'] == smoking]

    if cancer_type != 'all':
        filtered_df = filtered_df[filtered_df['Cancer_Type'] == cancer_type]

    filtered_df = filtered_df[filtered_df['Age'] >= min_age]

    # Group by country and calculate statistics
    country_stats = filtered_df.groupby('Country').agg(
        CaseCount=('Country', 'size'),
        AvgMortalityRisk=('Mortality_Risk', 'mean'),
        AvgSurvivalProb=('5_Year_Survival_Probability', 'mean')
    ).reset_index()

    # Create scatter geo plot
    fig = px.scatter_geo(
        country_stats,
        locations="Country",
        locationmode="country names",
        size="CaseCount",
        color="AvgMortalityRisk",
        hover_name="Country",
        hover_data=["CaseCount", "AvgMortalityRisk", "AvgSurvivalProb"],
        projection="natural earth",
        title="Global Distribution of Lung Cancer Cases and Mortality Risk",
        color_continuous_scale="RdYlGn_r",
        labels={
            "CaseCount": "Number of Cases",
            "AvgMortalityRisk": "Avg Mortality Risk",
            "AvgSurvivalProb": "Avg 5-Year Survival"
        }
    )

    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)