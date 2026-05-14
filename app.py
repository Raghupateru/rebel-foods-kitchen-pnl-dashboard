import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Kitchen PNL Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Kitchen PNL & Variance Dashboard")
st.markdown("Business Intelligence Dashboard for Kitchen Store Performance")

@st.cache_data
def load_data():
    df = pd.read_excel("Kittchen PNL Data.xlsx")

    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
        .str.replace("%", "PERCENT")
    )

    numeric_cols = [
        'ORDER_COUNT',
        'CART_SALES',
        'DISCOUNT',
        'NET_REVENUE',
        'IDEAL_FOOD_COST',
        'GROSS_MARGIN',
        'KITCHEN_EBITDA',
        'VARIANCE'
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['MONTH_DATE'] = pd.to_datetime(df['MONTH'], format='%b-%Y', errors='coerce')

    df['GM_PERCENT'] = (df['GROSS_MARGIN'] / df['NET_REVENUE']) * 100
    df['CM'] = df['GROSS_MARGIN'] - df['IDEAL_FOOD_COST']
    df['CM_PERCENT'] = (df['CM'] / df['NET_REVENUE']) * 100
    df['EBITDA_PERCENT'] = (df['KITCHEN_EBITDA'] / df['NET_REVENUE']) * 100
    df['VARIANCE_PERCENT'] = (df['VARIANCE'] / df['NET_REVENUE']) * 100

    revenue_bins = [0, 15e5, 25e5, 35e5, 45e5, np.inf]

    revenue_labels = [
        'Below INR 15 lacs',
        'INR 15 to 25 lacs',
        'INR 25 to 35 lacs',
        'INR 35 to 45 lacs',
        'Above INR 45 lacs'
    ]

    df['REVENUE_BUCKET'] = pd.cut(
        df['NET_REVENUE'],
        bins=revenue_bins,
        labels=revenue_labels
    )

    variance_bins = [-np.inf, 2, 3, 5, np.inf]

    variance_labels = [
        'Var <2%',
        'Var 2% to 3%',
        'Var 3% to 5%',
        'Var >5%'
    ]

    df['VARIANCE_BUCKET'] = pd.cut(
        df['VARIANCE_PERCENT'],
        bins=variance_bins,
        labels=variance_labels
    )

    return df

try:
    df = load_data()

except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

st.sidebar.header("Dashboard Filters")

store_filter = st.sidebar.multiselect(
    "Store",
    options=sorted(df['STORE'].dropna().unique()),
    default=sorted(df['STORE'].dropna().unique())
)

city_filter = st.sidebar.multiselect(
    "City",
    options=sorted(df['CITY'].dropna().unique()),
    default=sorted(df['CITY'].dropna().unique())
)

month_filter = st.sidebar.multiselect(
    "Month",
    options=sorted(df['MONTH'].dropna().unique()),
    default=sorted(df['MONTH'].dropna().unique())
)

revenue_cohort_filter = st.sidebar.multiselect(
    "Revenue Cohort",
    options=sorted(df['REVENUE_COHORT'].dropna().unique()),
    default=sorted(df['REVENUE_COHORT'].dropna().unique())
)

cm_cohort_filter = st.sidebar.multiselect(
    "CM Cohort",
    options=sorted(df['CM_COHORT'].dropna().unique()),
    default=sorted(df['CM_COHORT'].dropna().unique())
)

ebitda_category_filter = st.sidebar.multiselect(
    "EBITDA Category",
    options=sorted(df['EBITDA_CATEGORY'].dropna().unique()),
    default=sorted(df['EBITDA_CATEGORY'].dropna().unique())
)

revenue_range = st.sidebar.slider(
    "Net Revenue Range",
    float(df['NET_REVENUE'].min()),
    float(df['NET_REVENUE'].max()),
    (
        float(df['NET_REVENUE'].min()),
        float(df['NET_REVENUE'].max())
    )
)

cm_range = st.sidebar.slider(
    "CM % Range",
    float(df['CM_PERCENT'].min()),
    float(df['CM_PERCENT'].max()),
    (
        float(df['CM_PERCENT'].min()),
        float(df['CM_PERCENT'].max())
    )
)

ebitda_range = st.sidebar.slider(
    "EBITDA Range",
    float(df['KITCHEN_EBITDA'].min()),
    float(df['KITCHEN_EBITDA'].max()),
    (
        float(df['KITCHEN_EBITDA'].min()),
        float(df['KITCHEN_EBITDA'].max())
    )
)

variance_bucket_filter = st.sidebar.multiselect(
    "Variance Category",
    options=df['VARIANCE_BUCKET'].dropna().unique(),
    default=df['VARIANCE_BUCKET'].dropna().unique()
)

filtered_df = df[
    (df['STORE'].isin(store_filter)) &
    (df['CITY'].isin(city_filter)) &
    (df['MONTH'].isin(month_filter)) &
    (df['REVENUE_COHORT'].isin(revenue_cohort_filter)) &
    (df['CM_COHORT'].isin(cm_cohort_filter)) &
    (df['EBITDA_CATEGORY'].isin(ebitda_category_filter)) &
    (df['NET_REVENUE'].between(revenue_range[0], revenue_range[1])) &
    (df['CM_PERCENT'].between(cm_range[0], cm_range[1])) &
    (df['KITCHEN_EBITDA'].between(ebitda_range[0], ebitda_range[1])) &
    (df['VARIANCE_BUCKET'].isin(variance_bucket_filter))
]

kitchen_tab, variance_tab, insights_tab = st.tabs([
    "Kitchen PNL Dashboard",
    "Variance Dashboard",
    "Business Insights"
])

with kitchen_tab:

    st.header("Kitchen Level PNL Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    total_revenue = filtered_df['NET_REVENUE'].sum()
    total_ebitda = filtered_df['KITCHEN_EBITDA'].sum()
    avg_gm = filtered_df['GM_PERCENT'].mean()
    avg_variance = filtered_df['VARIANCE_PERCENT'].mean()

    col1.metric("Total Revenue", f"₹ {total_revenue:,.0f}")
    col2.metric("Total EBITDA", f"₹ {total_ebitda:,.0f}")
    col3.metric("Avg GM %", f"{avg_gm:.2f}%")
    col4.metric("Avg Variance %", f"{avg_variance:.2f}%")

    st.divider()

    revenue_trend = (
        filtered_df
        .groupby('MONTH', as_index=False)['NET_REVENUE']
        .sum()
    )

    fig1 = px.line(
        revenue_trend,
        x='MONTH',
        y='NET_REVENUE',
        markers=True,
        title='Monthly Revenue Trend'
    )

    st.plotly_chart(fig1, use_container_width=True)

    city_ebitda = (
        filtered_df
        .groupby('CITY', as_index=False)['KITCHEN_EBITDA']
        .sum()
        .sort_values(by='KITCHEN_EBITDA', ascending=False)
    )

    fig2 = px.bar(
        city_ebitda,
        x='CITY',
        y='KITCHEN_EBITDA',
        title='EBITDA by City'
    )

    st.plotly_chart(fig2, use_container_width=True)

    cohort_analysis = (
        filtered_df
        .groupby('REVENUE_COHORT', as_index=False)
        .agg({
            'NET_REVENUE': 'mean',
            'KITCHEN_EBITDA': 'mean',
            'STORE': 'count'
        })
    )

    st.subheader("Revenue Cohort Analysis")

    st.dataframe(
        cohort_analysis,
        use_container_width=True
    )

    st.subheader("Kitchen Snapshot")

    display_cols = [
        'MONTH',
        'CITY',
        'STORE',
        'NET_REVENUE',
        'GM_PERCENT',
        'CM_PERCENT',
        'KITCHEN_EBITDA',
        'VARIANCE_PERCENT'
    ]

    st.dataframe(
        filtered_df[display_cols],
        use_container_width=True,
        height=500
    )

with variance_tab:

    st.header("Variance Level PNL Dashboard")

    st.subheader("Sub-dashboard 1 — Average Variance % by Revenue Category")

    variance_summary = (
        filtered_df
        .groupby(['REVENUE_BUCKET', 'MONTH'])['VARIANCE_PERCENT']
        .mean()
        .reset_index()
    )

    variance_pivot = variance_summary.pivot(
        index='REVENUE_BUCKET',
        columns='MONTH',
        values='VARIANCE_PERCENT'
    )

    st.dataframe(
        variance_pivot.style.format('{:.2f}%'),
        use_container_width=True
    )

    fig3 = px.bar(
        variance_summary,
        x='REVENUE_BUCKET',
        y='VARIANCE_PERCENT',
        color='MONTH',
        barmode='group',
        title='Average Variance % by Revenue Category'
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    st.subheader("Sub-dashboard 2 — Kitchen Store Count by Revenue Category")

    store_summary = (
        filtered_df
        .groupby(['REVENUE_BUCKET', 'MONTH'])['STORE']
        .nunique()
        .reset_index(name='STORE_COUNT')
    )

    store_pivot = store_summary.pivot(
        index='REVENUE_BUCKET',
        columns='MONTH',
        values='STORE_COUNT'
    )

    st.dataframe(
        store_pivot,
        use_container_width=True
    )

    heatmap_data = store_pivot.fillna(0)

    fig4 = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='YlOrRd'
    ))

    fig4.update_layout(
        title='Store Count Heatmap'
    )

    st.plotly_chart(fig4, use_container_width=True)

with insights_tab:

    st.header("Business Insights")

    top_revenue = (
        filtered_df
        .groupby('STORE', as_index=False)['NET_REVENUE']
        .sum()
        .sort_values(by='NET_REVENUE', ascending=False)
        .head(10)
    )

    st.subheader("Top 10 Revenue Generating Stores")

    fig5 = px.bar(
        top_revenue,
        x='STORE',
        y='NET_REVENUE',
        title='Top Revenue Stores'
    )

    st.plotly_chart(fig5, use_container_width=True)

    low_ebitda = (
        filtered_df
        .groupby('STORE', as_index=False)['KITCHEN_EBITDA']
        .sum()
        .sort_values(by='KITCHEN_EBITDA')
        .head(10)
    )

    st.subheader("Lowest EBITDA Stores")

    fig6 = px.bar(
        low_ebitda,
        x='STORE',
        y='KITCHEN_EBITDA',
        title='Lowest EBITDA Stores'
    )

    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Revenue vs EBITDA Correlation")

    fig7 = px.scatter(
        filtered_df,
        x='NET_REVENUE',
        y='KITCHEN_EBITDA',
        color='CITY',
        hover_data=['STORE'],
        title='Revenue vs EBITDA'
    )

    st.plotly_chart(fig7, use_container_width=True)

    st.subheader("Key Business Observations")

    st.markdown("""
    - Stores with higher revenue cohorts generally show stronger EBITDA performance.
    - Some stores generate high revenue but weak EBITDA, indicating operational inefficiencies.
    - Variance above 5% should be monitored closely because it indicates potential wastage.
    - Revenue concentration exists across a few cities.
    - Stores with low CM% require pricing or cost optimization.
    """)

st.divider()

st.caption("Developed using Streamlit + Plotly")
