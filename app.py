#  import libaries.
import pandas as pd
import numpy as np
import streamlit as st
import plotly_express as px

# bring in the data.
df = pd.read_csv("Business_sales_EDA.csv", sep =";", index_col= "Product ID")
# clean the data
df= df.drop(columns =['brand', 'Product Category', 'currency', 'name', 'description', 'url', 'Seasonal'])
df.dropna(inplace = True)
# st.dataframe(df)
# st.write(df["season"])

# configuring the tittle
sidebar = st.sidebar
sidebar.title("Navigation section")
sidebar.info("Click Home to read about the data and Dashbord to explore the data")
page = sidebar.radio("Go to" , ["🏠 Home", "📊 Dashboard"])

# home page 
if page == "🏠 Home":
    st.title("🏠 Business Sales Dashboard Overview")
    st.markdown("""
    ### About the Dataset
    📊 This dataset contains sales information including:
    - Product attributes : Product Position, Promotion, Seasonal, Sales Volume, price, terms, section, season, material, origin.     
    - Sales metrics: Price and Sales Volume

    ### Purpose of the data
    This dashboard helps answer:
    1. Which season has the highest sales?
    2. Does Promotion affect sales or revenue?
    3. Which Product Positions generate the most revenue?
    4. Top-selling products by revenue.
    """)
    st.info("Use the Dashboard tab to explore.")
    st.stop()


# dashboard page
filter_cols = df.select_dtypes("O").columns
column = sidebar.selectbox("CHOOSE A COLUMN", filter_cols, index = None)
if column is not None:
    items = df[column].unique().tolist()
    item = sidebar.selectbox("CHOOSE AN ITEM", items, index = None)
else:
    item = None

# defign my function
def filter_data(df, column, item):
    if column is not None:
        if item is not None:
            filter_df = df[df[column] == item]
            return filter_df
    return df
filtered_df = filter_data(df, column , item)
filtered_df["Revenue"]= filtered_df["price"]*filtered_df["Sales Volume"]
# metrics
st.title("📈 Dashboard Metrics")
col1,col2,col3 = st.columns(3)
col1.metric(label = "💰Total Revenue", value= f'${round(filtered_df["Revenue"].sum()/1000000, 2)} M', border= True)
col2.metric(label = "📦Total Sales Volume", value= f'{round(filtered_df["Sales Volume"].sum()/1000000,2)} M', border= True)
col3.metric(label = "🛒Total Records", value=filtered_df.shape[0], border = True)

# col1.metric("💰 Total Revenue", f"${total_revenue:,.0f}", border = True)
# col2.metric("📦 Total Sales Volume", f'{total_sales}M', border= True)
# col3.metric("🛒 total_records", total_records, border = True)

st.markdown("""
### Insights:
- 💡 Total Revenue shows overall money earned.
- 📦 Total sales volume indicates number of product sold.
- 🛒 Total records shows total sales entries.
""")
# application of the header
if column is not None:
     st.title(f"Business Sales Analysis for ({item}) in {column.capitalize()}.")
elif column is not None and item is None:
    st.title(f"Business Sales Analysis for {column.capitalize()}.")
    st.info("Please choose an item to filter by")
else:
    st.header("Bussiness Sales Analysis.")
    st.info("Please select a column you want to filter in the side bar")
st.dataframe(filtered_df, use_container_width = True)

 # question 1
st.header("📊 Sales Volume by Season")
st.subheader("Which season has the highest sales?")


# Group by season and sum Sales Volume
season = (
    filtered_df.groupby("season")["Sales Volume"]
    .sum()
    .reset_index()
    .sort_values(by="Sales Volume", ascending=False)
)


season["Sales Volume"] = season["Sales Volume"].round(0).astype(int)

def format_units(x):
    if x >= 1000000000:  # Billions
        return f"{x / 1000000000:.2f}B units"
    elif x >= 1000000:    # Millions
        return f"{x / 1000000:.2f}M units"
    elif x >= 1000:        # Thousands
        return f"{x / 1000:.1f}K units"
    else:
        return f"{x:,} units"


season["Sales Volume (Formatted)"] = season["Sales Volume"].apply(format_units)

season_display = season[["season", "Sales Volume (Formatted)"]].copy()
season_display.columns = ["Season", "Total Units Sold"]

st.write("**Total Sales Volume by Season (Highest to Lowest):**")
st.dataframe(season_display, use_container_width=True, hide_index=True)

#graph
bar_fig = px.bar(
    season,
    x="season",
    y="Sales Volume",
    title="Sales Volume by Season",
    color="season",
    text = "Sales Volume"
)
pie_fig =px.pie(season, names="season", values = "Sales Volume", title = "Sales Volume Distribution by season")
col1, col2 = st.columns(2)
col1.plotly_chart(bar_fig, use_container_width=True)
col2.plotly_chart(pie_fig, use_container_width=True)

top_season = season.iloc[0]["season"].capitalize()
top_units = season.iloc[0]["Sales Volume (Formatted)"]
st.success(f"🏆 Highest sales volume: **{top_season}** with **{top_units}**")
st.markdown (""" This is a chart showing total number of unit sold(Sales Volume) for each season.
### key insights by season:
- Autumn : Highest Sales around 4 million units is the best Performing season.
- Winter : Second highest in the chart, about 3.2 to 3.3 million.
- Spring : Third and it is about 2.5 million.
- Summer : Lowest and it is about 2 million.""")

# question 2
st.header("🎉Effect of Promotion on Sales?")
# if "Promotion" in filtered_df.columns:
with_promotion =filtered_df[filtered_df["Promotion"] =="Yes"]["Sales Volume"].sum()
without_promotion = filtered_df[filtered_df["Promotion"] !="Yes"]["Sales Volume"].sum()
st.write("with_promotion the total sales : ", with_promotion, "units sold")
st.write("without_promotion the total sales : ", without_promotion, "units sold")

# pie chat
promo_data= pd.DataFrame({"Promotion":["with_promotion", "without_promotion"],"Sales Volume":[with_promotion, without_promotion]})
fig_pie =px.pie(promo_data,values = "Sales Volume",names= "Promotion", title = "Sales Distribution of With Promotion vs Without Promotion")
color_discrete_sequence= ["#FF6B6B", "#4ECDC4"]
# hole = 0.4,
fig_pie.update_traces(hole=0.4) 

fig_pie.update_traces(textposition= "inside",textinfo= "percent+label")

st.plotly_chart(fig_pie,use_container_width = True)
percent_increase = ((with_promotion - without_promotion)/without_promotion)*100
st.success(f"Yes! Promotion increase total sales volume by about {percent_increase:.1f}% 🎉")

# question 3
st.header("📦Which Product Positions generate the most revenue?")
filtered_df["Revenue"]= filtered_df["price"]*filtered_df["Sales Volume"]
# st.write(filtered_df.columns.tolist())
position= filtered_df.groupby("Product Position")["Revenue"].sum().reset_index().sort_values(by="Revenue", ascending = False)
st.write("Revenue by product position")

# Round to whole numbers and create a readable formatted column
position["Revenue"] = position["Revenue"].round(0).astype(int)

# format the numbers
def format_revenue(x):
    if x >= 1000000000:  # Billions
        return f"${x / 1000000000:.2f}B"
    elif x >= 1000000:    # Millions
        return f"${x / 1000000:.2f}M"
    elif x >= 1000:        # Thousands
        return f"${x / 1000:.1f}K"
    else:
        return f"${x:,}"

position["Revenue (Formatted)"] = position["Revenue"].apply(format_revenue)

position_display = position[["Product Position", "Revenue (Formatted)"]].copy()
position_display.columns = ["Product Position", "Total Revenue"]


st.dataframe(position_display, use_container_width=True, hide_index=True)


fig = px.bar(
    position,
    x="Product Position",
    y="Revenue",
    title="Revenue Generated by Product Position",
    color="Product Position",
    text="Revenue (Formatted)"
)
fig.update_traces(textposition="outside")
fig.update_layout(yaxis_title="Revenue", xaxis_title="Product Position")
st.plotly_chart(fig, use_container_width=True)


top_position = position.iloc[0]["Product Position"]
top_revenue = position.iloc[0]["Revenue (Formatted)"]
st.success(f"🏆 The highest revenue comes from **{top_position}** with **{top_revenue}**!")

# question 4
st.header("🏆 Top-Selling Products by Revenue")
# Calculate Revenue
filtered_df["Revenue"] = filtered_df["price"] * filtered_df["Sales Volume"]
# Group by Product Name (adjust column name if yours is different, e.g., 'Item' or 'Product')
top_products = (
    filtered_df.groupby("terms")["Revenue"]
    .sum()
    .reset_index()
    .sort_values(by="Revenue", ascending=False)
)

top_products["Revenue"] = top_products["Revenue"].round(0).astype(int)
def format_revenue(x):
    if x >= 1000000:
        return f"${x / 1000000:.2f}M"
    # elif x >= 1000000:
    #     return f"${x / 1000000:.2f}M"
    elif x >= 1_000:
        return f"${x / 1000:.1f}K"
    else:
        return f"${x:,}"

top_products["Total Revenue"] = top_products["Revenue"].apply(format_revenue)


display_df = top_products[["terms", "Total Revenue"]].copy()
st.subheader("Top Products by Revenue")
st.dataframe(display_df, use_container_width=True, hide_index=True)  # Top 10

# Bar chart
fig = px.bar(
    top_products,
    x="terms",
    y="Revenue",
    title="Top 10 Products by Revenue",
    color="terms",
    text="Total Revenue"
)
fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True)

top_product = top_products.iloc[0]["terms"]
top_rev = top_products.iloc[0]["Total Revenue"]
st.success(f"🏆 number1 Top Seller: **{top_product}** with **{top_rev}** in revenue!")




