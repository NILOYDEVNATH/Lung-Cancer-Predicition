from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from tab_content import risk_factor_tab_content, survival_tab_content

# Initialize the app
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

# Country mapping for ISO codes
country_map = {
    'USA': 'USA', 'UK': 'GBR', 'DR Congo': 'COD', 'Russia': 'RUS', 'Thailand': 'THA',
    'Colombia': 'COL', 'Egypt': 'EGY', 'Spain': 'ESP', 'Kenya': 'KEN', 'Japan': 'JPN',
    'Bangladesh': 'BGD', 'Nigeria': 'NGA', 'Pakistan': 'PAK', 'Myanmar': 'MMR',
    'South Africa': 'ZAF', 'Indonesia': 'IDN', 'Italy': 'ITA', 'Germany': 'DEU',
    'Brazil': 'BRA', 'Tanzania': 'TZA', 'South Korea': 'KOR', 'Turkey': 'TUR',
    'Vietnam': 'VNM', 'Iran': 'IRN', 'China': 'CHN', 'Mexico': 'MEX', 'India': 'IND',
    'Philippines': 'PHL', 'France': 'FRA', 'Ethiopia': 'ETH'
}

# Define a color scheme
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
    # Header with improved styling
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

    # Main Content
    html.Div([
        # Left Panel: Filters with improved styling
        html.Div([
            html.Div([
                html.H4("🔍 Filter Data",
                        style={'marginBottom': '20px', 'fontSize': '16px', 'color': color_theme['primary']}),

                # Continent Filter
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
                ], style={'marginBottom': '20px'}),

                # Country Filter Store
                dcc.Store(id='map-filter', data='all'),

                # Smoking Status Filter
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
                ], style={'marginBottom': '20px'}),

                # Cancer Type Filter
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
                ], style={'marginBottom': '20px'}),

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
                ], style={'marginBottom': '20px'}),

                # Age Range Slider
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
            })
        ], style={
            'width': '280px',
            'marginRight': '20px',
            'flexShrink': 0
        }),

        # Right Panel: Main Content
        html.Div([
            html.Div(id='dashboard-content')
        ], style={'flex': 1})
    ], style={
        'display': 'flex',
        'padding': '20px',
        'backgroundColor': color_theme['background']
    })
])


# Improved geographic visualization
def create_geographic_content(df):
    df['iso_alpha3'] = df['Country'].map(country_map)

    # Aggregate data with more metrics
    country_stats = df.groupby(['Country', 'iso_alpha3', 'Continent']).agg({
        'Age': 'mean',
        'Mortality_Risk': 'mean',
        '5_Year_Survival_Probability': 'mean',
        'Country': 'count'
    }).rename(columns={'Country': 'Count'}).reset_index()

    # Create enhanced map
    fig = px.scatter_geo(
        country_stats,
        locations='iso_alpha3',
        color='Continent',
        hover_name='Country',
        size='Count',
        hover_data={
            'Age': ':.1f',
            'Mortality_Risk': ':.3f',
            '5_Year_Survival_Probability': ':.3f',
            'Count': True
        },
        projection='natural earth',
        title='Global Distribution of Lung Cancer Cases',
        labels={
            'Age': 'Avg Age',
            'Mortality_Risk': 'Avg Mortality Risk',
            '5_Year_Survival_Probability': 'Avg 5-Year Survival',
            'Count': 'Number of Cases'
        }
    )

    fig.update_layout(
        height=500,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        dragmode='select',
        font={'size': 12},
        title_font={'size': 20},
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        )
    )

    # Add summary statistics
    total_cases = df.shape[0]
    countries_count = df['Country'].nunique()
    avg_survival = df['5_Year_Survival_Probability'].mean()

    summary_cards = html.Div([
        html.Div([
            html.H3(f"{total_cases:,}", style={'margin': '0', 'color': color_theme['primary']}),
            html.P("Total Cases", style={'margin': '0', 'fontSize': '12px'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        html.Div([
            html.H3(f"{countries_count}", style={'margin': '0', 'color': color_theme['secondary']}),
            html.P("Countries", style={'margin': '0', 'fontSize': '12px'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        html.Div([
            html.H3(f"{avg_survival:.1%}", style={'margin': '0', 'color': color_theme['tertiary']}),
            html.P("Avg 5-Year Survival", style={'margin': '0', 'fontSize': '12px'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(3, 1fr)', 'gap': '15px', 'marginBottom': '20px'})

    return html.Div([
        summary_cards,
        dcc.Graph(
            id='geographic-tab',
            figure=fig,
            config={'displayModeBar': True, 'displaylogo': False}
        )
    ])


# Improved risk factors visualization
def create_risk_factors_content(df):
    # Create a more comprehensive risk analysis
    risk_plots = html.Div([
        # Air Pollution vs Mortality Risk
        html.Div([
            dcc.Graph(
                figure=px.violin(
                    df,
                    x='Air_Pollution_Exposure',
                    y='Mortality_Risk',
                    color='Air_Pollution_Exposure',
                    box=True,
                    points="outliers",
                    title="Mortality Risk by Air Pollution Level",
                    category_orders={"Air_Pollution_Exposure": ['Low', 'Medium', 'High']},
                    color_discrete_sequence=px.colors.sequential.Oranges
                ).update_layout(
                    showlegend=False,
                    height=400,
                    title_font={'size': 16}
                )
            )
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),

        # Smoking Status vs Mortality Risk
        html.Div([
            dcc.Graph(
                figure=px.violin(
                    df,
                    x='Smoking_Status',
                    y='Mortality_Risk',
                    color='Smoking_Status',
                    box=True,
                    points="outliers",
                    title="Mortality Risk by Smoking Status",
                    category_orders={"Smoking_Status": ['Non-Smoker', 'Former Smoker', 'Smoker']},
                    color_discrete_sequence=px.colors.sequential.Reds
                ).update_layout(
                    showlegend=False,
                    height=400,
                    title_font={'size': 16}
                )
            )
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),

        # Combined Risk Heatmap
        html.Div([
            dcc.Graph(
                figure=create_risk_heatmap(df),
                config={'displayModeBar': True, 'displaylogo': False}
            )
        ], style={'width': '100%', 'padding': '10px'})
    ])

    return risk_plots


def create_risk_heatmap(df):
    # Create a correlation matrix of risk factors
    risk_factors = ['Air_Pollution_Exposure', 'Smoking_Status', 'Family_History', 'Mortality_Risk']

    # Convert categorical to numeric for correlation
    df_numeric = df.copy()
    df_numeric['Air_Pollution_Exposure'] = df_numeric['Air_Pollution_Exposure'].map({'Low': 1, 'Medium': 2, 'High': 3})
    df_numeric['Smoking_Status'] = df_numeric['Smoking_Status'].map({'Non-Smoker': 1, 'Former Smoker': 2, 'Smoker': 3})
    df_numeric['Family_History'] = df_numeric['Family_History'].map({'No': 0, 'Yes': 1})

    # Create pivot table
    pivot_data = df.groupby(['Air_Pollution_Exposure', 'Smoking_Status'])['Mortality_Risk'].mean().reset_index()
    pivot_table = pivot_data.pivot(index='Air_Pollution_Exposure', columns='Smoking_Status', values='Mortality_Risk')

    fig = px.imshow(
        pivot_table,
        labels=dict(x="Smoking Status", y="Air Pollution Exposure", color="Avg Mortality Risk"),
        x=['Non-Smoker', 'Former Smoker', 'Smoker'],
        y=['Low', 'Medium', 'High'],
        color_continuous_scale='YlOrRd',
        title="Risk Factor Interaction: Smoking × Air Pollution"
    )

    fig.update_layout(
        height=400,
        title_font={'size': 16}
    )

    return fig


# Improved survival analysis
def create_survival_content(df):
    survival_plots = html.Div([
        # Distribution plots
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=px.histogram(
                        df,
                        x='Mortality_Risk',
                        nbins=30,
                        title="Mortality Risk Distribution",
                        color_discrete_sequence=[color_theme['quaternary']]
                    ).update_layout(
                        showlegend=False,
                        height=350,
                        title_font={'size': 16},
                        xaxis_title="Mortality Risk",
                        yaxis_title="Number of Patients",
                        bargap=0.1
                    )
                )
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),

            html.Div([
                dcc.Graph(
                    figure=px.histogram(
                        df,
                        x='5_Year_Survival_Probability',
                        nbins=30,
                        title="5-Year Survival Probability Distribution",
                        color_discrete_sequence=[color_theme['tertiary']]
                    ).update_layout(
                        showlegend=False,
                        height=350,
                        title_font={'size': 16},
                        xaxis_title="5-Year Survival Probability",
                        yaxis_title="Number of Patients",
                        bargap=0.1
                    )
                )
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'})
        ]),

        # Family History Impact
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=px.box(
                        df,
                        x="Family_History",
                        y="5_Year_Survival_Probability",
                        color="Family_History",
                        title="Impact of Family History on Survival",
                        notched=True,
                        color_discrete_sequence=[color_theme['secondary'], color_theme['primary']]
                    ).update_layout(
                        showlegend=False,
                        height=350,
                        title_font={'size': 16}
                    )
                )
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),

            # Survival by Cancer Type
            html.Div([
                dcc.Graph(
                    figure=px.strip(
                        df,
                        x="Cancer_Type",
                        y="5_Year_Survival_Probability",
                        color="Cancer_Type",
                        title="Survival Probability by Cancer Type",
                        color_discrete_sequence=px.colors.qualitative.Set2
                    ).update_layout(
                        showlegend=False,
                        height=350,
                        title_font={'size': 16}
                    )
                )
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'})
        ]),

        # Mutation Impact
        html.Div([
            dcc.Graph(
                figure=create_mutation_survival_plot(df),
                config={'displayModeBar': True, 'displaylogo': False}
            )
        ], style={'width': '100%', 'padding': '10px'})
    ])

    return survival_plots


def create_mutation_survival_plot(df):
    # Create enhanced mutation survival plot
    df_mutation = df[df['Mutation_Type'].notna()]

    fig = px.box(
        df_mutation,
        x="Mutation_Type",
        y="5_Year_Survival_Probability",
        color="Mutation_Type",
        title="Survival Probability by Mutation Type",
        notched=True,
        color_discrete_sequence=px.colors.qualitative.Safe
    )

    fig.update_layout(
        showlegend=False,
        height=400,
        title_font={'size': 16},
        xaxis_title="Mutation Type",
        yaxis_title="5-Year Survival Probability"
    )

    return fig


# Main callback
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

    return html.Div([
        # Geographic Section
        html.Div([
            html.H2("Geographic Distribution",
                    style={'fontSize': '22px', 'marginBottom': '15px', 'color': color_theme['text']}),
            create_geographic_content(filtered_df)
        ], style={'marginBottom': '30px', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

        # Risk Factors Section
        html.Div([
            html.H2("Risk Factors Analysis",
                    style={'fontSize': '22px', 'marginBottom': '15px', 'color': color_theme['text']}),
            create_risk_factors_content(filtered_df)
        ], style={'marginBottom': '30px', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

        # Survival Section
        html.Div([
            html.H2("Survival Analysis",
                    style={'fontSize': '22px', 'marginBottom': '15px', 'color': color_theme['text']}),
            create_survival_content(filtered_df)
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
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


# Keep existing callbacks for continent/country filtering
@app.callback(
    Output('continent-filter', 'options'),
    Output('continent-filter', 'value'),
    Input('map-filter', 'data')
)
def update_continent_options(selected_country):
    if selected_country == 'all':
        options = [{'label': 'All', 'value': 'all'}] + [{'label': c, 'value': c} for c in data['continents']]
        value = 'all'
    else:
        continent = country_to_continent.get(selected_country, 'all')
        options = [{'label': continent, 'value': continent}]
        value = continent

    return options, value


@app.callback(
    Output('map-filter', 'data'),
    Input('geographic-tab', 'selectedData')
)
def update_country_filter(selected_data):
    if selected_data and 'points' in selected_data:
        selected_countries = [point['hovertext'] for point in selected_data['points']]
        return ', '.join(selected_countries)
    return 'all'


# Run the app
if __name__ == '__main__':
    app.run(debug=True)