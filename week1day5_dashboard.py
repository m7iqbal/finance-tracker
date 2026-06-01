import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import redis
import json

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Personal Finance Dashboard")
st.markdown("Tracking my monthly income and expenses — May 2026")

# --- DARK MODE TOGGLE ---
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)

if dark_mode:
    st.markdown("""
        <style>
            .stApp {
                background-color: #1a1a2e;
                color: #ffffff;
            }
            .stMetric {
                background-color: #16213e;
                border-radius: 10px;
                padding: 10px;
            }
            .stDataFrame {
                background-color: #16213e;
            }
            section[data-testid="stSidebar"] {
                background-color: #0f3460;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            .stApp {
                background-color: #ffffff;
                color: #000000;
            }
            section[data-testid="stSidebar"] {
                background-color: #f0f2f6;
            }
        </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
#@st.cache_data  # caches data so it doesn't reload every click
#def load_data():
#    engine = create_engine("postgresql://postgres:123424722599189@localhost/finance_tracker")
#    df = pd.read_sql("SELECT * FROM transactions", engine)
#    df["date"] = pd.to_datetime(df["date"])
#    return df

#df = load_data()

#st.success(f"✅ Loaded {len(df)} transactions from PostgreSQL")

# Connect to Redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

@st.cache_data(ttl=60)
def load_data():
    cache_key = "transactions_all"

    cached = r.get(cache_key)
    if cached:
        df = pd.DataFrame(json.loads(cached))
        df["date"] = pd.to_datetime(df["date"])
        return df

    engine = create_engine("postgresql://postgres:123424722599189@localhost/finance_tracker")
    df = pd.read_sql("SELECT * FROM transactions", engine)
    df["date"] = pd.to_datetime(df["date"])

    r.setex(cache_key, 60, df.to_json(orient="records"))
    return df

# ← ADD THIS LINE — you were missing this!
df = load_data()

st.success(f"✅ Loaded {len(df)} transactions from PostgreSQL")

# --- CALCULATE SUMMARY ---
total_income   = df[df["amount"] > 0]["amount"].sum()
total_expenses = df[df["amount"] < 0]["amount"].abs().sum()
net_balance    = total_income - total_expenses
biggest_expense = df[df["amount"] < 0]["amount"].min()

# --- SUMMARY CARDS ---
st.markdown("---")
st.subheader("📊 Monthly Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="💵 Total Income", value=f"RM {total_income:,.2f}")

with col2:
    st.metric(label="💸 Total Expenses", value=f"RM {total_expenses:,.2f}")

with col3:
    st.metric(label="🏦 Net Balance", value=f"RM {net_balance:,.2f}",
              delta=f"RM {net_balance:,.2f} remaining")

with col4:
    st.metric(label="🔴 Biggest Expense", value=f"RM {abs(biggest_expense):,.2f}")

# --- FILTER SIDEBAR ---
st.sidebar.title("🔍 Filters")

# Category filter
all_categories = ["All"] + sorted(df["category"].unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", all_categories)

# Transaction type filter
transaction_type = st.sidebar.radio(
    "Show",
    ["All", "Expenses Only", "Income Only"]
)

# Date range filter
st.sidebar.markdown("---")
min_date = df["date"].min().date()
max_date = df["date"].max().date()
date_range = st.sidebar.date_input(
    "Filter by Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# -----------------------------------------------
# APPLY FILTERS — must come AFTER all sidebar code
# -----------------------------------------------
filtered_df = df.copy()                           # step 1 — start with all data

if selected_category != "All":                    # step 2 — category filter
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

if transaction_type == "Expenses Only":           # step 3 — type filter
    filtered_df = filtered_df[filtered_df["amount"] < 0]
elif transaction_type == "Income Only":
    filtered_df = filtered_df[filtered_df["amount"] > 0]

if len(date_range) == 2:                          # step 4 — date filter
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["date"].dt.date >= start_date) &
        (filtered_df["date"].dt.date <= end_date)
    ]

# --- TABLE + DOWNLOAD ---
st.markdown("---")
st.subheader("📋 Transaction Details")
st.dataframe(
    filtered_df[["date", "description", "category", "amount"]],
    use_container_width=True
)
st.caption(f"Showing {len(filtered_df)} transactions")

st.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False),
    file_name="transactions_filtered.csv",
    mime="text/csv"
)

# --- CHARTS ---
st.markdown("---")
st.subheader("📈 Visual Analysis")

col_left, col_right = st.columns(2)

# --- LEFT: Bar chart ---
with col_left:
    st.markdown("**Spending by Category**")
    category_summary = (
        df[df["amount"] < 0]
        .groupby("category")["amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
        .reset_index()
    )
    category_summary.columns = ["category", "total_spent"]

    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.barplot(data=category_summary, x="category", y="total_spent",
                palette="Blues_d", ax=ax1)
    ax1.set_xlabel("")
    ax1.set_ylabel("RM")
    for i, row in category_summary.iterrows():
        ax1.text(i, row["total_spent"] + 3,
                 f"RM{row['total_spent']:.0f}", ha="center", fontsize=9)
    plt.tight_layout()
    st.pyplot(fig1)

# --- RIGHT: Pie chart ---
with col_right:
    st.markdown("**Spending Breakdown**")
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    ax2.pie(
        category_summary["total_spent"],
        labels=category_summary["category"],
        autopct="%1.1f%%",
        startangle=140,
        colors=sns.color_palette("pastel")
    )
    plt.tight_layout()
    st.pyplot(fig2)

# --- BOTTOM: Timeline ---
st.markdown("**Expense Timeline**")
expenses_only = df[df["amount"] < 0].sort_values("date")
average_value = expenses_only["amount"].abs().mean()

fig3, ax3 = plt.subplots(figsize=(12, 4))
ax3.plot(expenses_only["date"], expenses_only["amount"].abs(),
         marker="o", color="#e74c3c", linewidth=2)
ax3.axhline(y=average_value, color="blue", linestyle="--",
            label=f"Avg: RM {average_value:.2f}")
for _, row in expenses_only.iterrows():
    ax3.annotate(row["description"],
                 (row["date"], abs(row["amount"])),
                 textcoords="offset points",
                 xytext=(0, 10), ha="center", fontsize=8, rotation=30)
ax3.set_xlabel("Date")
ax3.set_ylabel("RM")
ax3.legend()
plt.tight_layout()
st.pyplot(fig3)

# --- COMMITMENT BREAKDOWN ---
st.markdown("---")
st.subheader("🔒 Commitment Breakdown")

commitment_df = df[df["category"] == "Commitment"]
commitment_breakdown = (
    commitment_df[commitment_df["amount"] < 0]
    .groupby("description")["amount"]
    .sum()
    .abs()
    .reset_index()
)
commitment_breakdown.columns = ["description", "total_spent"]

col_a, col_b = st.columns(2)

with col_a:
    fig4, ax4 = plt.subplots(figsize=(7, 7))
    ax4.pie(commitment_breakdown["total_spent"],
            labels=commitment_breakdown["description"],
            autopct="%1.1f%%",
            startangle=140,
            colors=sns.color_palette("pastel"))
    ax4.set_title("Where does Commitment money go?")
    plt.tight_layout()
    st.pyplot(fig4)

with col_b:
    st.markdown("**Commitment Details**")
    st.dataframe(commitment_breakdown, use_container_width=True)
    total_commitment = commitment_breakdown["total_spent"].sum()
    st.metric("Total Commitment", f"RM {total_commitment:,.2f}",
              delta=f"{(total_commitment/total_income*100):.1f}% of income")