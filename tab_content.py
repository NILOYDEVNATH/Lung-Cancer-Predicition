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
####################################################
def generate_geographic_map_figure(df_filtered, country_iso_map=country_map):
    df_processed = df_filtered.copy()
    df_processed['iso_alpha3'] = df_processed['Country'].map(country_iso_map)

    # Aggregate data
    agg_dict = {
        'Age': 'mean',
        'Mortality_Risk': 'mean',
        '5_Year_Survival_Probability': 'mean',
        'Country': 'count'
    }

    country_stats = df_processed.groupby(
        ['Country', 'iso_alpha3', 'Continent'], observed=True
    ).agg(agg_dict).rename(columns={'Country': 'Count'}).reset_index()

    country_stats = country_stats.rename(columns={
        'Age': 'Average Age',
        'Mortality_Risk': 'Mortality Risk',
        '5_Year_Survival_Probability': '5-Year Survival Probability'
    })

    country_stats['customdata'] = list(zip(
        country_stats['Count'],
        country_stats['Average Age'],
        country_stats['Mortality Risk'],
        country_stats['5-Year Survival Probability']
    ))

    fig = px.scatter_geo(
        country_stats,
        locations='iso_alpha3',
        color='Continent',
        hover_name='Country',
        size='Count',
        projection='natural earth'
    )

    fig.update_traces(
        customdata=country_stats['customdata'],
        hovertemplate=(
            "<b>%{hovertext}</b><br><br>"
            "Individuals: %{customdata[0]:,}<br>"
            "Avg. Age: %{customdata[1]:.1f} yrs<br>"
            "Avg. Mortality Risk: %{customdata[2]:.1%}<br>"
            "Avg. 5yr Survival: %{customdata[3]:.1%}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        dragmode='select',
        clickmode='event+select'
    )

    fig.update_geos(
        visible=True,
        resolution=110,
        scope="world",
        bgcolor='rgba(0,0,0,0)',
        lakecolor='rgb(255, 255, 255)'
    )

    return fig


def generate_smoking_risk_figure(df_filtered):
    # Calculate average mortality risk for each smoking status
    avg_mortality_by_smoking = df_filtered.groupby('Smoking_Status')['Mortality_Risk'].mean().reset_index()

    # Overall average mortality risk
    overall_avg_mortality = df_filtered['Mortality_Risk'].mean()

    # Create violin plot with clearer title
    fig = px.violin(
        df_filtered,
        x='Smoking_Status',
        y='Mortality_Risk',
        title="How Smoking Affects Mortality Risk",
        category_orders={"Smoking_Status": ['Non-Smoker', 'Former Smoker', 'Smoker']},
        labels={
            'Smoking_Status': 'Smoking Status',
            'Mortality_Risk': 'Mortality Risk (0-1)'
        },
        box=True,  # Show box plot inside violin
        points=False,  # Don't show individual points
        color='Smoking_Status',
        color_discrete_map={
            'Non-Smoker': '#2ca02c',  # Green
            'Former Smoker': '#ff7f0e',  # Orange
            'Smoker': '#d62728'  # Red
        }
    )

    # Add average reference line
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=overall_avg_mortality,
        x1=2.5,
        y1=overall_avg_mortality,
        line=dict(color="black", width=1.5, dash="dash"),
    )

    # Add annotation for average
    fig.add_annotation(
        x=2.5,
        y=overall_avg_mortality,
        text=f"Overall average: {overall_avg_mortality:.2f}",
        showarrow=False,
        font=dict(size=10),
        xshift=45,
        align="left"
    )

    # Add annotation for smokers risk
    smoker_avg = \
    avg_mortality_by_smoking[avg_mortality_by_smoking['Smoking_Status'] == 'Smoker']['Mortality_Risk'].values[0]
    nonsmoker_avg = \
    avg_mortality_by_smoking[avg_mortality_by_smoking['Smoking_Status'] == 'Non-Smoker']['Mortality_Risk'].values[0]

    # Calculate the percentage increase
    pct_increase = ((smoker_avg - nonsmoker_avg) / nonsmoker_avg) * 100

    # Add annotation highlighting the difference
    fig.add_annotation(
        x="Smoker",
        y=smoker_avg,
        text=f"{pct_increase:.0f}% higher risk than non-smokers",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-40,
        font=dict(color="red", size=10),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="red",
        borderwidth=1
    )

    # Clean layout
    fig.update_layout(
        margin=dict(l=60, r=20, t=60, b=50),
        hovermode='x unified',
        yaxis_title='Mortality Risk (0-1)',
        showlegend=False,
        title_font=dict(size=14)
    )

    # Update hover template
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Mortality Risk: %{y:.2f}<br><extra></extra>"
    )

    return fig



def generate_age_dist_figure(df_filtered):
    fig = px.histogram(
        df_filtered,
        x="Age",
        title="Age Distribution of Lung Cancer Patients",
        labels={'Age': 'Age (years)', 'count': 'Number of Patients'},
        opacity=0.8,
        color_discrete_sequence=['#1f77b4']  # Use a consistent blue color
    )

    # Calculate and show the average age
    avg_age = df_filtered['Age'].mean()

    # Add a vertical line for average age
    fig.add_vline(
        x=avg_age,
        line_width=2,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Average: {avg_age:.1f} years",
        annotation_position="top right"
    )

    # Highlight high-risk age groups (example: over 65)
    high_risk_age = 65

    # Add annotation for high-risk age groups
    fig.add_annotation(
        x=high_risk_age,
        y=0.95,
        yref="paper",
        text="Higher risk age group",
        showarrow=True,
        arrowhead=1,
        arrowcolor="red",
        ax=0,
        ay=-30,
        font=dict(size=10, color="red"),
        bordercolor="red",
        borderwidth=1,
        bgcolor="white"
    )

    fig.update_traces(
        hovertemplate=(
            "Age: %{x}<br>"
            "Number of Patients: %{y}<extra></extra>"
        )
    )

    fig.update_layout(
        margin=dict(l=50, r=20, t=50, b=40),
        bargap=0.1,
        title_font=dict(size=14)
    )

    return fig


def generate_gender_pie_figure(df_filtered):
    # Gender Breakdown
    gender_counts = df_filtered.groupby('Gender', observed=True).size().reset_index(name='Count')

    fig = px.pie(
        gender_counts,
        values='Count',
        names='Gender',
        title="Gender Distribution",
        labels={'Gender': 'Gender', 'Count': 'Number of Patients'}
    )

    fig.update_layout(
        margin=dict(l=50, r=20, t=50, b=40)
    )

    fig.update_traces(
        hovertemplate=(
            "Gender: %{label}<br>"
            "Number of Patients: %{value}<br>"
            "Percent: %{percent}<extra></extra>"
        )
    )

    return fig


def generate_family_history_impact_figure(df_filtered):
    # Overall average survival probability
    overall_avg_survival = df_filtered['5_Year_Survival_Probability'].mean()

    # Create a more informative violin plot
    fig = px.violin(
        df_filtered,
        x="Family_History",
        y="5_Year_Survival_Probability",
        title="How Family History Affects Survival Chance",
        color="Family_History",
        color_discrete_map={
            'Yes': '#d62728',  # Red for presence of family history
            'No': '#2ca02c'  # Green for absence
        },
        box=True,  # Show box plot inside violin
        points=False  # Don't show individual points
    )

    # Add average reference line
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=overall_avg_survival,
        x1=1.5,
        y1=overall_avg_survival,
        line=dict(color="black", width=1.5, dash="dash"),
    )

    # Add annotation for average
    fig.add_annotation(
        x=1.5,
        y=overall_avg_survival,
        text=f"Overall average: {overall_avg_survival:.2f}",
        showarrow=False,
        font=dict(size=10),
        xshift=50,
        align="left"
    )

    # Calculate impact of family history
    avg_survival_with_history = df_filtered[df_filtered['Family_History'] == 'Yes'][
        '5_Year_Survival_Probability'].mean()
    avg_survival_without_history = df_filtered[df_filtered['Family_History'] == 'No'][
        '5_Year_Survival_Probability'].mean()

    # Add comparison annotation
    if avg_survival_with_history < avg_survival_without_history:
        diff_pct = ((avg_survival_without_history - avg_survival_with_history) / avg_survival_with_history) * 100
        fig.add_annotation(
            x="Yes",
            y=avg_survival_with_history,
            text=f"{diff_pct:.0f}% lower survival rate",
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=40,
            font=dict(color="red", size=10),
            bgcolor="rgba(255,255,255,0.8)",
            borderwidth=1
        )

    fig.update_layout(
        margin=dict(l=50, r=20, t=50, b=40),
        yaxis_title="5-Year Survival Probability (0-1)",
        xaxis_title="Family History of Lung Cancer",
        showlegend=False,
        title_font=dict(size=14)
    )

    # Update hover template
    fig.update_traces(
        hovertemplate="<b>Family History: %{x}</b><br>5-Year Survival: %{y:.2f}<br><extra></extra>"
    )

    # Add key insight
    fig.add_annotation(
        x=0.5,
        y=1.05,
        xref="paper",
        yref="paper",
        text="Early screening is crucial for those with family history",
        showarrow=False,
        font=dict(size=10, color="black"),
        align="center",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="red",
        borderwidth=1,
        borderpad=4
    )

    return fig

def generate_ses_figure(df_filtered):
    # SES vs. Cancer Stage (grouped bar chart)
    fig = px.histogram(
        df_filtered,
        x="Socioeconomic_Status",
        color="Stage_at_Diagnosis",
        barmode='group',
        title="Cancer Stage at Diagnosis by Socioeconomic Status",  # Changed from "by Income Level"
        category_orders={"Socioeconomic_Status": ["Low", "Middle", "High"]},
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={
            "Socioeconomic_Status": "Socioeconomic Status",  # Changed from "Income Level"
            "Stage_at_Diagnosis": "Cancer Stage"
        }
    )

    # Count cases by SES and stage
    stage_counts = df_filtered.groupby(['Socioeconomic_Status', 'Stage_at_Diagnosis']).size().reset_index(name='Count')

    # Find the percentage of late-stage diagnoses in Low SES
    low_ses_df = stage_counts[stage_counts['Socioeconomic_Status'] == 'Low']
    if not low_ses_df.empty:
        late_stages = ['Stage III', 'Stage IV']
        low_ses_late = low_ses_df[low_ses_df['Stage_at_Diagnosis'].isin(late_stages)]['Count'].sum()
        low_ses_total = low_ses_df['Count'].sum()

        if low_ses_total > 0:
            late_pct = (low_ses_late / low_ses_total) * 100

            # Add annotation showing the high percentage of late diagnoses
            fig.add_annotation(
                x="Low",
                y=low_ses_late,
                text=f"{late_pct:.0f}% diagnosed at late stages",
                showarrow=True,
                arrowhead=1,
                ax=0,
                ay=-30,
                font=dict(color="red", size=10),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="red",
                borderwidth=1
            )

    fig.update_layout(
        margin=dict(l=50, r=20, t=50, b=40),
        bargap=0.1,
        xaxis_title="Socioeconomic Status",  # Changed from "Income Level"
        yaxis_title="Number of Patients",
        legend_title="Cancer Stage",
        title_font=dict(size=14),
        showlegend=False  # Remove legend as requested
    )

    # Removed the insight annotation as requested

    fig.update_traces(
        hovertemplate=(
            "Stage: %{fullData.name}<br>"
            "Socioeconomic Status: %{x}<br>"  # Changed from "Income Level"
            "Number of Patients: %{y}<extra></extra>"
        )
    )

    # Make sure no text shows up in unwanted places
    fig.update_xaxes(ticktext=["Low", "Middle", "High"])

    return fig




def generate_treatment_acces_figure(df_filtered):
    # Treatment Access vs. Survival
    fig = px.violin(
        df_filtered,
        x="Treatment_Access",
        y="5_Year_Survival_Probability",
        title="5-Year Survival Probability by Treatment Access",
        category_orders={"Treatment_Access": ["None", "Partial", "Full"]},
        color="Treatment_Access",
        color_discrete_map={
            "None": "#d62728",  # Red
            "Partial": "#ff7f0e",  # Orange
            "Full": "#2ca02c"  # Green
        },
        labels={
            "Treatment_Access": "Access to Treatment",
            "5_Year_Survival_Probability": "5-Year Survival Rate (0-1)"
        },
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
    avg_mortality_risk = np.nanmean(df_filtered['Mortality_Risk']) * 100
    avg_survival_prob = np.nanmean(df_filtered['5_Year_Survival_Probability']) * 100
    avg_age = np.nanmean(df_filtered['Age'])

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
