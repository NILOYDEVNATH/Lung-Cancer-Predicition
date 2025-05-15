from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

from tab_content import geographic_tab_content, risk_factor_tab_content, survival_tab_content

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
            ],style={
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

    return html.Div([
        # Geographic Section
        html.Div([
            html.H3("Geographic Distribution", style={'fontSize': '18px', 'marginBottom': '10px'}),
            geographic_tab_content(filtered_df)
        ], style={'marginBottom': '30px'}),

        # Risk Factors Section
        html.Div([
            html.H3("Risk Factors Analysis", style={'fontSize': '18px', 'marginBottom': '10px'}),
            risk_factor_tab_content(filtered_df)
        ], style={'marginBottom': '30px'}),

        # Survival Section
        html.Div([
            html.H3("Survival Analysis", style={'fontSize': '18px', 'marginBottom': '10px'}),
            survival_tab_content(filtered_df)
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


@app.callback(
    Output('map-filter', 'data'),
    Input('geographic-tab', 'selectedData')
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