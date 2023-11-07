import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime as dt
from babel.numbers import format_currency

sns.set(style='dark')
# performa penjualan dan revenue
def create_revenue_orders_df(df):
    revenue_orders_df = df.groupby(['year_month','year','month_no','month']).agg({
        "payment_value": "sum",
        "order_id": "count",
    }).sort_values(['year','month_no'], ascending=True).reset_index()    
    return revenue_orders_df

# kategori populer dan tidak
def create_populer_kategori_df(df):
    sum_order_items_df = df.groupby("product_category_name").product_id.count().sort_values(ascending=False).reset_index()
    sum_order_items_df = sum_order_items_df.rename(columns={"product_category_name": "category", "product_id": "orders"})
    return sum_order_items_df

# tipe pembayaran dan rata2 pembayaran
def create_tipe_pembayaran_df(df):
    type_payment_df = df.groupby(['payment_type']).agg({
        "payment_value": "mean",
        "order_id" : "nunique",
    }).sort_values(['order_id'], ascending=False).reset_index()
    return type_payment_df

# hari paling banyak transaksi
def create_popular_day_df(df):
    best_day_df = main_df.groupby(by="day").order_id.nunique().sort_values(ascending=False).reset_index()
    best_day_df.rename(columns={
        "order_id": "total_orders"
    }, inplace=True)
    return best_day_df

# RFM
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "count",
        "payment_value": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# load berkas all_data.csv sebagai sebuah DataFrame
all_df = pd.read_csv("dashboard/main_data.csv")

# mengurutkan DataFrame berdasarkan order_purchase_timestamp serta memastikan bertipe datetime
datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# filter dengan widget date input serta menambahkan logo perusahaan pada sidebar
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value = min_date,
        max_value = max_date,
        value=[min_date, max_date]
    )

# start_date dan end_date di atas akan digunakan untuk memfilter all_df. Data yang telah difilter ini selanjutnya akan disimpan dalam main_df
main_df = all_df[(pd.to_datetime(all_df["order_purchase_timestamp"]).dt.date >= start_date) & 
                (pd.to_datetime(all_df["order_purchase_timestamp"]).dt.date <= end_date)]

# memanggil helper function yang telah kita buat sebelumnya
revenue_orders_df =  create_revenue_orders_df(main_df)
populer_kategori_df = create_populer_kategori_df(main_df)
tipe_pembayaran_df = create_tipe_pembayaran_df(main_df)
popular_day_df = create_popular_day_df(main_df)
rfm_df = create_rfm_df(main_df)

# menambahkan header pada dashboard
st.header('Dicoding Collection Dashboard :sparkles:')

# menampilkan total order per bulan
st.subheader('Total Orders dan Revenue per bulan')

total_order = revenue_orders_df.order_id.sum()
st.metric("Total order", value=total_order)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    revenue_orders_df["year_month"],
    revenue_orders_df["order_id"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

# menampilkan total revenue per bulan
total_revenue = format_currency(revenue_orders_df.payment_value.sum(), "R$", locale='pt_BR') 
st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    revenue_orders_df["year_month"],
    revenue_orders_df["payment_value"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

# menampilkan 5 produk paling laris dan paling sedikit terjual
st.subheader("5 Kategori populer dan tidak")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#D3D3D3", "#D3D3D4", "#D3D3D5", "#D3D3D6", "#D3D3D7"]
 
sns.barplot(x="orders", y="category", data=populer_kategori_df.head(5), hue=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="orders", y="category", data=populer_kategori_df.sort_values(by="orders", ascending=True).head(5), hue=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)

# menapilkan tipe pembayaran dan rata2 pembayarannya
st.subheader("Tipe pembayaran populer dan rata-rata pembayarannya")

col1, col2 = st.columns(2)
 
with col1:
    tipe_pembayaran_rata = format_currency(tipe_pembayaran_df['payment_value'].iloc[0], "R$", locale='pt_BR') 
    st.metric("Rata-rata pembayaran", value=tipe_pembayaran_rata)
 
with col2:
    tipe_pembayaran = tipe_pembayaran_df['payment_type'].iloc[0]
    st.metric("Tipe Pembayaran", value=tipe_pembayaran)

labels = tipe_pembayaran_df['payment_type']
sizes = tipe_pembayaran_df['order_id']
explode = (0, 0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=45)
ax1.axis('equal') 

st.pyplot(fig1)

# menapilkan hari yang paling banyak transaksi
st.subheader("Hari dengan transaksi terbanyak")
col1, col2 = st.columns(2)
 
with col1:
    best_day = popular_day_df['day'].iloc[0]
    st.metric("Hari dengan transaksi terbanyak", value=best_day)

fig, ax = plt.subplots()
 
colors = ["#72BCD3", "#72BCD4", "#72BCD5", "#72BCD6", "#73BCD6", "#74BCD6", "#75BCD6"]
 
sns.barplot(x="day", y="total_orders", data=popular_day_df.sort_values(by="total_orders", ascending = False), hue=colors)
ax.set_ylabel("nilai transaksi")
ax.set_xlabel(None)
ax.set_title("Hari paling banyak transaksi", loc="center")
ax.tick_params(axis='y')
ax.tick_params(axis='x')

st.pyplot(fig)

# menampilkan nilai average atau rata-rata dari RFM (Recency, Frequency, & Monetary) parameter menggunakan widget metric()
st.subheader("Best Customer Based on RFM Parameters")
         
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "R$", locale='pt_BR') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#72BCD4", "#72BCD5", "#72BCD6", "#73BCD4", "#74BCD4"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), hue=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), hue=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), hue=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)
 
st.caption('Copyright (c) Dicoding 2023')
