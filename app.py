import streamlit as st

import pandas as pd
import numpy as np

from sqlalchemy import create_engine, inspect
from sqlalchemy import text

import altair as alt

warehouse = "postgresql://duckdb_sample_user:i6iKJc6FCs4hVS3AX6yMZngxJvMkzGCs@dpg-d0b2efp5pdvs73c9pi00-a/duckdb_sample"
engine = create_engine(warehouse,  client_encoding='utf8')
connection = engine.connect()

@st.cache_data
def load_data():
    query_ext = """
        SELECT *
        FROM sales_data_duckdb;
    """
    result = connection.execute(text(query_ext))
    return pd.DataFrame(result.mappings().all())

df = load_data()

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

st.title("Sales Dashboard")
st.markdown(":violet-badge[:material/star: This dashboard provides an overview of the sales data.]")

st.divider()

m1, m2, m3 = st.columns(3)
with m1:
    total_revenue = (df['Price Each'] * df['Quantity Ordered']).sum()
    st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")
with m2:
    total_orders = df['Order ID'].nunique()
    st.metric(label="Total Orders", value=total_orders)
with m3:
    total_products = df['Product'].nunique()
    st.metric(label="Total Products", value=total_products)

st.divider()

st.subheader("Total Sales Over Time")
df['Sales'] = df['Price Each'] * df['Quantity Ordered']
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Date'] = df['Order Date'].dt.date
sales_over_time = df.groupby('Date')['Sales'].sum().reset_index()
sales_over_time_chart = alt.Chart(sales_over_time).mark_line().encode(
    x='Date:T',
    y='Sales:Q'
).properties(
    width=700,
    height=400
)
st.altair_chart(sales_over_time_chart, use_container_width=True)

st.subheader("Sales by Product")
sales_by_product = df.groupby('Product')['Sales'].sum().reset_index()
sales_by_product = sales_by_product.sort_values(by='Sales', ascending=False)
sales_by_product_chart = alt.Chart(sales_by_product).mark_bar().encode(
    x=alt.X('Product:N', sort='-y'),
    y='Sales:Q'
).properties(
    width=700,
    height=400
)
st.altair_chart(sales_by_product_chart, use_container_width=True)

column1, column2 = st.columns(2)
with column1:
    st.subheader("Sales by Country")
    sales_by_country = df.groupby('Country')['Sales'].sum().reset_index()
    sales_by_country_chart = alt.Chart(sales_by_country).mark_arc().encode(
        theta=alt.Theta(field="Sales", type="quantitative"),
        color=alt.Color(field="Country", type="nominal"),
        tooltip=[alt.Tooltip(field="Country", type="nominal"), alt.Tooltip(field="Sales", type="quantitative")]
    ).properties(
        width=700,
        height=400
    )
    st.altair_chart(sales_by_country_chart, use_container_width=True)

    st.subheader("Top Products in Canada")
    df_canada = df[df['Country'] == 'Canada']
    top_products_canada = df_canada.groupby('Product')['Quantity Ordered'].sum().reset_index()
    top_products_canada = top_products_canada.sort_values(by='Quantity Ordered', ascending=False).head(10)
    top_products_canada_chart = alt.Chart(top_products_canada).mark_bar().encode(
        x='Quantity Ordered:Q',
        y=alt.X('Product:N', sort='-x'),
    ).properties(
        width=700,
        height=400
    )
    st.altair_chart(top_products_canada_chart, use_container_width=True)

with column2:
    st.subheader("Sales by State")
    df_usa = df[df['Country'] == 'USA']
    df_usa['State'] = df_usa['Purchase Address'].str.split(",").str[2].str.strip().str.split(" ").str[0]
    sales_by_state = df_usa.groupby('State')['Sales'].sum().reset_index()
    sales_by_state_chart = alt.Chart(sales_by_state).mark_arc().encode(
        theta=alt.Theta(field="Sales", type="quantitative"),
        color=alt.Color(field="State", type="nominal"),
        tooltip=[alt.Tooltip(field="State", type="nominal"), alt.Tooltip(field="Sales", type="quantitative")]
    ).properties(
        width=700,
        height=400
    )
    st.altair_chart(sales_by_state_chart, use_container_width=True)

    st.subheader("Top Products in USA")
    top_products_usa = df_usa.groupby('Product')['Quantity Ordered'].sum().reset_index()
    top_products_usa = top_products_usa.sort_values(by='Quantity Ordered', ascending=False).head(10)
    top_products_usa_chart = alt.Chart(top_products_usa).mark_bar().encode(
        x='Quantity Ordered:Q',
        y=alt.X('Product:N', sort='-x'),
    ).properties(
        width=700,
        height=400
    )
    st.altair_chart(top_products_usa_chart, use_container_width=True)
