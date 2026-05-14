import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Kitchen Dashboard", layout="wide")

st.title("Kitchen PNL Dashboard")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_excel("Kittchen PNL Data.xlsx")

    # Use first row as header
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)

    # Clean column names
    df.columns = [
        str(col).strip().replace(" ", "_")
        for col in df.columns
    ]

    return df

df = load_data()

# Show columns for debugging
st.subheader("Dataset Columns")
st.write(df.columns)

# Sidebar filters
store_filter = st.sidebar.multiselect(
    "Store",
    options=df["STORE"].dropna().unique(),
    default=df["STORE"].dropna().unique()
)

month_filter = st.sidebar.multiselect(
    "Month",
    options=df["MONTH"].dropna().unique(),
    default=df["MONTH"].dropna().unique()
)

filtered_df = df[
    (df["STORE"].isin(store_filter)) &
    (df["MONTH"].isin(month_filter))
]

# KPIs
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Total Revenue",
        f"{filtered_df['NET_REVENUE'].astype(float).sum():,.0f}"
    )

with col2:
    st.metric(
        "Total EBITDA",
        f"{filtered_df['KITCHEN_EBITDA'].astype(float).sum():,.0f}"
    )

# Table
st.subheader("Kitchen PNL Table")
st.dataframe(filtered_df)

# Revenue Chart
chart_data = filtered_df.groupby(
    "MONTH",
    as_index=False
)["NET_REVENUE"].sum()

chart_data["NET_REVENUE"] = chart_data["NET_REVENUE"].astype(float)

fig = px.bar(
    chart_data,
    x="MONTH",
    y="NET_REVENUE",
    title="Revenue by Month"
)

st.plotly_chart(fig, use_container_width=True)
