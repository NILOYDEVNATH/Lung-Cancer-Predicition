from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

from tab_content import demographic_tab_content, risk_factor_tab_content, geographic_tab_content, healthcare_tab_content, survival_tab_content

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

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Lung Cancer Risk Analysis", style={'textAlign': 'center'}),
    # Filters
    html.Div([
        html.Div([
            html.Label("Filter by Continent:"),
            dcc.Dropdown(
                id='continent-filter',
                options=[{'label': 'All', 'value': 'all'}] +
                        [{'label': c, 'value': c} for c in data['continents']],
                value='all'
            ),
        ], style={'width': '15%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '10px'}),
        html.Div([
            html.Label("Filter by Country:"),
            dcc.Dropdown(
                id='country-filter',
                options=[{'label': 'All', 'value': 'all'}] +
                        [{'label': c, 'value': c} for c in data['countries']],
                value='all'
            )
        ], style={'width': '15%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '10px'}),
        html.Div([
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
        ], style={'width': '15%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '10px'}),

        html.Div([
            html.Label("Filter by Cancer Type:"),
            dcc.Dropdown(
                id='cancer-type-filter',
                options=[{'label': 'All', 'value': 'all'}] +
                        [{'label': ct, 'value': ct} for ct in data['cancer_types']],
                value='all'
            ),
        ], style={'width': '15%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '10px'}),

        html.Div([
            html.Label("Minimum Age:"),
            dcc.RangeSlider(
                id='age-range-slider',
                min=int(df['Age'].min()),
                max=int(df['Age'].max()),
                value=[int(df['Age'].min()), int(df['Age'].max())],
                marks={i: str(i) for i in range(int(df['Age'].min()), int(df['Age'].max()) + 1, 10)},
                step=1,
                tooltip={"placement": "bottom", "always_visible": True}
            ),
        ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '10px'}),
    ],
    style={'padding': '10px 0px 10px 0px'}),
        # Navigation Tabs
        dcc.Tabs(id='tabs', value='geographic', children=[
            dcc.Tab(label='Geographic Analysis', value='geographic'),
            dcc.Tab(label='Demographics', value='demographics'),
            dcc.Tab(label='Risk Factors', value='risk_factors'),
            dcc.Tab(label='Healthcare Impact', value='healthcare'),
            dcc.Tab(label='Survival Analysis', value='survival'),
        ]),
    ]),

    # Content
    html.Div(id='tabs-content')
])

# Callback to render the selected tab content
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
     Input('continent-filter', 'value'),
     Input('country-filter','value'),
     Input('smoking-filter', 'value'),
     Input('cancer-type-filter', 'value'),
     Input('age-range-slider', 'value')]
)
def render_tab(tab, continent, country, smoking, cancer_type, age_range):

    filtered_df = filter_data(df, continent, country, smoking, cancer_type, age_range)
    if tab == 'demographics':
        return demographic_tab_content(filtered_df)
    elif tab == 'risk_factors':
        return risk_factor_tab_content(filtered_df)
    elif tab == 'geographic':
        return geographic_tab_content(filtered_df)
    elif tab == 'healthcare':
        return healthcare_tab_content(filtered_df)
    elif tab == 'survival':
        return survival_tab_content(filtered_df)

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

def filter_data(df, continent, country, smoking, cancer_type, age_range):
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

    filtered_df = filtered_df[
        (filtered_df['Age'] >= min_age) & (filtered_df['Age'] <= max_age)
        ]

    return filtered_df


@app.callback(
    Output('continent-filter', 'options'),  # Update the continent dropdown options
    Output('continent-filter', 'value'),  # Optionally reset the value of the continent dropdown
    Input('country-filter', 'value')  # When the country filter value changes
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

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
