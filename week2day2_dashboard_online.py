import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide"
)

# --- DARK MODE ---
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)

if dark_mode:
    st.markdown("""
        <style>
            .stApp { background-color: #1a1a2e; color: #ffffff; }
            section[data-testid="stSidebar"] { background-color: #0f3460; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            .stApp { background-color: #ffffff; color: #000000; }
            section[data-testid="stSidebar"] { background-color: #f0f2f6; }
        </style>
    """, unsafe_allow_html=True)

st.title("💰 Personal Finance Dashboard")
st.markdown("Tracking my monthly income and expenses — May 2026")

# --- LOAD DATA FROM CSV ---
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("transactions.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()
st.success(f"✅ Loaded {len(df)} transactions")

# --- SUMMARY ---
total_income    = df[df["amount"] > 0]["amount"].sum()
total_expenses  = df[df["amount"] < 0]["amount"].abs().sum()
net_balance     = total_income - total_expenses
biggest_expense = df[df["amount"] < 0]["amount"].min()

# --- CARDS ---
st.markdown("---")
st.subheader("📊 Monthly Summary")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💵 Total Income",    f"RM {total_income:,.2f}")
with col2:
    st.metric("💸 Total Expenses",  f"RM {total_expenses:,.2f}")
with col3:
    st.metric("🏦 Net Balance",     f"RM {net_balance:,.2f}",
              delta=f"RM {net_balance:,.2f} remaining")
with col4:
    st.metric("🔴 Biggest Expense", f"RM {abs(biggest_expense):,.2f}")

# --- SIDEBAR FILTERS ---
st.sidebar.title("🔍 Filters")

all_categories = ["All"] + sorted(df["category"].unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", all_categories)

transaction_type = st.sidebar.radio(
    "Show",
    ["All", "Expenses Only", "Income Only"]
)

st.sidebar.markdown("---")
min_date   = df["date"].min().date()
max_date   = df["date"].max().date()
date_range = st.sidebar.date_input(
    "Filter by Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# --- APPLY FILTERS ---
filtered_df = df.copy()

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

if transaction_type == "Expenses Only":
    filtered_df = filtered_df[filtered_df["amount"] < 0]
elif transaction_type == "Income Only":
    filtered_df = filtered_df[filtered_df["amount"] > 0]

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["date"].dt.date >= start_date) &
        (filtered_df["date"].dt.date <= end_date)
    ]

# --- TABLE ---
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

category_summary = (
    df[df["amount"] < 0]
    .groupby("category")["amount"]
    .sum()
    .abs()
    .sort_values(ascending=False)
    .reset_index()
)
category_summary.columns = ["category", "total_spent"]

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("**Spending by Category**")
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.barplot(data=category_summary, x="category",
                y="total_spent", palette="Blues_d", ax=ax1)
    ax1.set_xlabel("")
    ax1.set_ylabel("RM")
    for i, row in category_summary.iterrows():
        ax1.text(i, row["total_spent"] + 3,
                 f"RM{row['total_spent']:.0f}",
                 ha="center", fontsize=9)
    plt.tight_layout()
    st.pyplot(fig1)

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

# --- TIMELINE ---
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
                 xytext=(0, 10), ha="center",
                 fontsize=8, rotation=30)
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

# --- FOOTER ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: grey; font-size: 12px;'>
    Built by Iqbal Horan · 
    <a href='https://github.com/m7iqbal/finance-tracker'>GitHub</a>
    </div>
""", unsafe_allow_html=True)