from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

from tab_content import demographic_tab_content, risk_factor_tab_content, geographic_tab_content, \
    healthcare_tab_content, survival_tab_content, geographic_choose_menu_content, country_map

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
        html.H1("Lung Cancer Risk Analysis", style={'textAlign': 'center', 'fontSize': '24px', 'marginBottom': '10px'})
    ]),

    # Main Row: Sidebar + Tabs/Content
    html.Div([

        # --- Sidebar Filters ---
        html.Div([
            html.H5("Filters", style={'marginBottom': '10px', 'fontSize': '14px'}),

            html.Div([

                # Continent
                html.Div([
                    html.Label("Continent:", style={'fontSize': '12px'}),
                    dcc.RadioItems(
                        id='continent-filter',
                        options=[{'label': '🌍 All', 'value': 'all'}] + [{'label': c, 'value': c} for c in data['continents']],
                        value='all',
                        labelStyle={
                            'display': 'inline-block', 'padding': '4px 6px', 'margin': '2px',
                            'border': '1px solid #ddd', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '11px'
                        },
                        inputStyle={'marginRight': '5px'}
                    )
                ], style={'marginBottom': '10px'}),

                # Country (map)
                html.Div([
                    dcc.Store(id='map-filter', data='all'),
                    geographic_choose_menu_content(df)
                ], style={'marginBottom': '10px'}),

                # Smoking
                html.Div([
                    html.Label("Smoking:", style={'fontSize': '12px'}),
                    dcc.RadioItems(
                        id='smoking-filter',
                        options=[
                            {'label': '🚭 Non', 'value': 'Non-Smoker'},
                            {'label': '🫁 Former', 'value': 'Former Smoker'},
                            {'label': '🚬 Smoker', 'value': 'Smoker'},
                            {'label': 'All', 'value': 'all'}
                        ],
                        value='all',
                        labelStyle={
                            'display': 'inline-block', 'padding': '4px 6px', 'margin': '2px',
                            'border': '1px solid #ddd', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '11px'
                        },
                        inputStyle={'marginRight': '5px'}
                    )
                ], style={'marginBottom': '10px'}),

                # Cancer Type
                html.Div([
                    html.Label("Cancer Type:", style={'fontSize': '12px'}),
                    dcc.RadioItems(
                        id='cancer-type-filter',
                        options=[{'label': 'All', 'value': 'all'}] + [{'label': ct, 'value': ct} for ct in data['cancer_types']],
                        value='all',
                        labelStyle={
                            'display': 'inline-block', 'padding': '4px 6px', 'margin': '2px',
                            'border': '1px solid #ddd', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '11px'}
                        ,
                        inputStyle={'marginRight': '5px'}
                    )
                ], style={'marginBottom': '10px'}),

                # Sex Filter
                html.Div([
                    html.Label("Sex:", style={'fontSize': '12px'}),
                    dcc.RadioItems(
                        id='sex-filter',
                        options=[
                            {'label': '👩 Female', 'value': 'Female'},
                            {'label': '👨 Male', 'value': 'Male'},
                            {'label': 'All', 'value': 'all'}
                        ],
                        value='all',
                        labelStyle={
                            'display': 'inline-block', 'padding': '4px 6px', 'margin': '2px',
                            'border': '1px solid #ddd', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '11px'
                        },
                        inputStyle={'marginRight': '5px'}
                    )
                ], style={'marginBottom': '10px'}),

                # Age Range
                html.Div([
                    html.Label("Age Range:", style={'fontSize': '12px'}),
                    dcc.RangeSlider(
                        id='age-range-slider',
                        min=int(df['Age'].min()),
                        max=int(df['Age'].max()),
                        value=[int(df['Age'].min()), int(df['Age'].max())],
                        marks={i: str(i) for i in range(int(df['Age'].min()), int(df['Age'].max()) + 1, 10)},
                        step=1,
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ])
            ])
        ], style={
            'width': '250px',
            'padding': '15px',
            'border': '1px solid #eee',
            'borderRadius': '6px',
            'backgroundColor': '#f8f8f8',
            'marginRight': '15px',
            'flexShrink': 0
        }),

        # --- Main Content Area ---
        html.Div([
            dcc.Tabs(id='tabs', value='geographic', children=[
                dcc.Tab(label='Geographic', value='geographic'),
                dcc.Tab(label='Demographics', value='demographics'),
                dcc.Tab(label='Risk Factors', value='risk_factors'),
                dcc.Tab(label='Healthcare', value='healthcare'),
                dcc.Tab(label='Survival', value='survival'),
            ], style={'fontSize': '12px'}),

            html.Div(id='tabs-content', style={'marginTop': '10px'})
        ], style={'flex': 1})
    ], style={'display': 'flex', 'alignItems': 'flex-start'})
])

# Callback to render the selected tab content
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
     Input('continent-filter', 'value'),
     Input('map-filter', 'data'),
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

@app.callback(
    Output('map-filter', 'data'),
    Input('geographic-map', 'selectedData')
)
def update_country_filter(selected_data):
    if selected_data and 'points' in selected_data:
        selected_countries = [point['hovertext'] for point in selected_data['points']]
        print(f"Selected countries: {selected_countries}")
        return ', '.join(selected_countries)
    return 'all'

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
