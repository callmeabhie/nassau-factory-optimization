
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Nassau Candy Dashboard",
    page_icon="🍬",
    layout="wide"
)

st.title("Nassau Candy Distributor")
st.subheader("Factory Reallocation & Shipping Optimization")
st.caption("Sales and profitability analysis")

@st.cache_data
def load_data():
    df = pd.read_csv("Nassau Candy Distributor.csv")
    factories = pd.read_csv("factory_locations.csv")
    mapping = pd.read_csv("proposed_product_factory_mapping.csv")

    for col in ["Sales", "Gross Profit", "Cost", "Units"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df, factories, mapping

try:
    df, factories, mapping = load_data()
except Exception as e:
    st.error(f"Could not load project files: {e}")
    st.stop()

st.sidebar.header("Filters")

regions = sorted(df["Region"].dropna().unique())
selected_regions = st.sidebar.multiselect(
    "Select regions",
    regions,
    default=regions
)

filtered = df[df["Region"].isin(selected_regions)].copy()

if filtered.empty:
    st.warning("Select at least one region.")
    st.stop()

sales = filtered["Sales"].sum()
profit = filtered["Gross Profit"].sum()
cost = filtered["Cost"].sum()
units = filtered["Units"].sum()
margin = profit / sales * 100 if sales > 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"{sales:,.2f}")
c2.metric("Gross Profit", f"{profit:,.2f}")
c3.metric("Total Cost", f"{cost:,.2f}")
c4.metric("Units Sold", f"{units:,.0f}")

st.metric("Gross Profit Margin", f"{margin:.2f}%")

tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Product Analysis",
    "Factory Assignments",
    "Data Explorer"
])

with tab1:
    st.subheader("Sales by Region")
    regional = (
        filtered.groupby("Region", as_index=False)
        .agg(Sales=("Sales", "sum"),
             Gross_Profit=("Gross Profit", "sum"))
    )

    st.plotly_chart(
        px.bar(regional, x="Region", y="Sales",
               title="Sales by Region"),
        use_container_width=True
    )

    st.plotly_chart(
        px.bar(regional, x="Region", y="Gross_Profit",
               title="Gross Profit by Region"),
        use_container_width=True
    )

with tab2:
    st.subheader("Product Profitability")
    products = (
        filtered.groupby("Product Name", as_index=False)
        .agg(Sales=("Sales", "sum"),
             Gross_Profit=("Gross Profit", "sum"),
             Units=("Units", "sum"))
        .sort_values("Gross_Profit", ascending=False)
    )

    st.plotly_chart(
        px.bar(products.head(10),
               x="Gross_Profit", y="Product Name",
               title="Top 10 Products by Gross Profit"),
        use_container_width=True
    )

    st.dataframe(products, use_container_width=True)

with tab3:
    st.warning(
        "Factory assignments are proposed and have not been "
        "validated as optimal. Shipping costs, distances, "
        "and factory capacity still need verification."
    )

    st.subheader("Proposed Product Assignments")
    st.dataframe(mapping, use_container_width=True)

    st.subheader("Candidate Factory Locations")
    st.dataframe(factories, use_container_width=True)

with tab4:
    st.subheader("Filtered Dataset")
    st.dataframe(filtered, use_container_width=True)

    st.download_button(
        "Download filtered data",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="nassau_filtered_data.csv",
        mime="text/csv"
    )

st.divider()
st.caption(
    "Historical sales and profit do not prove that factory "
    "reallocation will reduce costs. Date fields require validation."
)
