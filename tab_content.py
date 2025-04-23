from dash import dcc, html
import plotly.express as px

country_map = {
            'USA': 'USA', 'UK': 'GBR', 'DR Congo': 'COD', 'Russia': 'RUS', 'Thailand': 'THA',
            'Colombia': 'COL', 'Egypt': 'EGY', 'Spain': 'ESP', 'Kenya': 'KEN', 'Japan': 'JPN',
            'Bangladesh': 'BGD', 'Nigeria': 'NGA', 'Pakistan': 'PAK', 'Myanmar': 'MMR',
            'South Africa': 'ZAF', 'Indonesia': 'IDN', 'Italy': 'ITA', 'Germany': 'DEU',
            'Brazil': 'BRA', 'Tanzania': 'TZA', 'South Korea': 'KOR', 'Turkey': 'TUR',
            'Vietnam': 'VNM', 'Iran': 'IRN', 'China': 'CHN', 'Mexico': 'MEX', 'India': 'IND',
            'Philippines': 'PHL', 'France': 'FRA', 'Ethiopia': 'ETH'
        }

def demographic_tab_content(df):
    return html.Div([
        html.Div([
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
                        df.groupby('Gender', observed=True).size().reset_index(name='Count'),
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
                        df.groupby('Continent', observed=True).size().reset_index(name='Count'),
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
                        df.groupby('Cancer_Type', observed=True).size().reset_index(name='Count'),
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
                        df[df['Mutation_Type'].notna()].groupby('Mutation_Type', observed=True).size().reset_index(name='Count'),
                        x='Mutation_Type',
                        y='Count',
                        color='Mutation_Type',
                        title="Distribution by Mutation Type",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                )
            ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
        ])
    ])


def risk_factor_tab_content(df):
    return html.Div([
        # Risk Factor Analysis Section
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
    ])

def geographic_tab_content(df):

    df['iso_alpha3'] = df['Country'].map(country_map)

    country_stats = df.groupby(['Country', 'iso_alpha3', 'Continent']).agg({
        'Age': 'mean',
        'Mortality_Risk': 'mean',
        '5_Year_Survival_Probability': 'mean',
        'Country': 'count'
    }).rename(columns={'Country': 'Count'}).reset_index()

    fig = px.scatter_geo(
        country_stats,
        locations='iso_alpha3',
        color='Continent',
        hover_name='Country',
        size='Count',  # Size of bubble based on number of cases
        hover_data=['Age', 'Mortality_Risk', '5_Year_Survival_Probability'],
        projection='natural earth',
    )

    fig.update_layout(
        height=400,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        dragmode='select'
    )

    return html.Div([
        dcc.Graph(
            id = 'geographic-tab',
            figure=fig)
    ])

def healthcare_tab_content(df):
    return html.Div([

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

        # Second row - Additional Healthcare Analysis
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
        ])
    ])

def survival_tab_content(df):
    return html.Div([

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

        # Second row - Additional Survival Analysis
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

def geographic_choose_menu_content(df):
        df['iso_alpha3'] = df['Country'].map(country_map)

        # Aggregate data
        country_stats = df.groupby(['Country', 'iso_alpha3']).agg(
            Count=('Country', 'count')
        ).reset_index()

        fig = px.scatter_geo(
            country_stats,
            locations='iso_alpha3',
            hover_name='Country',
            size='Count',
            color_discrete_sequence=['#888'],
        )

        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><extra></extra>",
            marker=dict(sizemode='area', sizeref=100, sizemin=2)
        )

        fig.update_layout(
            autosize=True,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            height=None,
            geo=dict(bgcolor='rgba(0,0,0,0)'),
            clickmode = 'event+select'
        )

        return html.Div([
            dcc.Graph(
                id='geographic-map',
                figure=fig,
                config={
                    'displayModeBar': False,
                    'staticPlot': False
                },
                style={
                    'width': '100%',
                    'aspectRatio': '2',
                    'overflow': 'hidden'
                }
            )
        ])

