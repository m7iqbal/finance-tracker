import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# --- Load from PostgreSQL ---
engine = create_engine("postgresql://postgres:123424722599189@localhost/finance_tracker")
df = pd.read_sql("SELECT * FROM transactions", engine)
df["date"] = pd.to_datetime(df["date"])

# --- Setup seaborn style (makes everything look nicer) ---
sns.set_theme(style="whitegrid")

# --- CHART 1: Spending by Category (Bar Chart) ---
category_summary = (
    df[df["amount"] < 0]
    .groupby("category")["amount"]
    .sum()
    .abs()
    .sort_values(ascending=False)
    .reset_index()
)
category_summary.columns = ["category", "total_spent"]

plt.figure(figsize=(10, 6))
sns.barplot(data=category_summary, x="category", y="total_spent", palette="Reds_d")

plt.title("Total Spending by Category", fontsize=16, fontweight="bold")
plt.xlabel("Category", fontsize=12)
plt.ylabel("Total Spent (RM)", fontsize=12)

# Add value labels on top of each bar
for i, row in category_summary.iterrows():
    plt.text(i, row["total_spent"] + 5, f"RM {row['total_spent']:.0f}", 
             ha="center", fontsize=10)

plt.tight_layout()
plt.savefig("chart1_category.png")   # saves as image file
plt.show()
print("✅ Chart 1 saved")

# --- CHART 2: Spending breakdown (Pie Chart) ---
# --- CHALLENGE ---
commitment_df = df[df["category"] == "Commitment"]

commitment_breakdown = (
    commitment_df[commitment_df["amount"] < 0]
    .groupby("description")["amount"]
    .sum()
    .abs()
    .reset_index()
)
commitment_breakdown.columns = ["description", "total_spent"]
# --- CHALLENGE ---

plt.figure(figsize=(8, 8))

plt.pie(
    #category_summary["total_spent"],
    commitment_breakdown["total_spent"],
    #labels=category_summary["category"],
    labels=commitment_breakdown["description"],
    autopct="%1.1f%%",        # shows percentage on each slice
    startangle=140,
    colors=sns.color_palette("pastel")
)

#plt.title("Spending Breakdown by Category", fontsize=16, fontweight="bold")
#plt.tight_layout()
#plt.savefig("chart2_pie.png")
#plt.show()
#print("✅ Chart 2 saved")

#challenge
plt.title("Commitment Breakdown", fontsize=16, fontweight="bold")
plt.tight_layout()
plt.savefig("chart_commitment_pie.png")
plt.show()
print("✅ Commitment pie chart saved")

# --- CHART 3: Income vs Total Expenses ---
total_income   = df[df["amount"] > 0]["amount"].sum()
total_expenses = df[df["amount"] < 0]["amount"].abs().sum()
net_balance    = total_income - total_expenses

summary_df = pd.DataFrame({
    "type":   ["Income", "Expenses", "Net Balance"],
    "amount": [total_income, total_expenses, net_balance]
})

colors = ["#2ecc71", "#e74c3c", "#3498db"]  # green, red, blue

plt.figure(figsize=(8, 5))
bars = plt.barh(summary_df["type"], summary_df["amount"], color=colors)

# Add value labels
for bar, val in zip(bars, summary_df["amount"]):
    plt.text(bar.get_width() + 20, bar.get_y() + bar.get_height() / 2,
             f"RM {val:.2f}", va="center", fontsize=11)

plt.title("Income vs Expenses Overview", fontsize=16, fontweight="bold")
plt.xlabel("Amount (RM)", fontsize=12)
plt.tight_layout()
plt.savefig("chart3_overview.png")
plt.show()
print("✅ Chart 3 saved")

# --- CHART 4: Transaction amounts over time (Timeline Chart) ---
expenses_only = df[df["amount"] < 0].sort_values("date")

# Calculate average BEFORE using it
average_value = expenses_only["amount"].abs().mean()

plt.figure(figsize=(12, 5))
plt.plot(expenses_only["date"], expenses_only["amount"].abs(),
         marker="o", color="#e74c3c", linewidth=2, markersize=8)

# Add the average line
plt.axhline(y=average_value, color='blue', linestyle='--', 
            label=f"Avg: RM {average_value:.2f}")

# Label each point
for _, row in expenses_only.iterrows():
    plt.annotate(
        row["description"],
        (row["date"], abs(row["amount"])),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
        fontsize=8,
        rotation=30
    )

plt.title("Expense Timeline", fontsize=16, fontweight="bold")
plt.xlabel("Date", fontsize=12)
plt.ylabel("Amount (RM)", fontsize=12)
plt.legend()
plt.tight_layout()
plt.savefig("chart4_timeline.png")
plt.show()
print("✅ Chart 4 saved")

# --- CHART 5: All charts in one figure ---
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle("Personal Finance Dashboard — May 2026", 
             fontsize=20, fontweight="bold")

# Top Left — Bar chart
sns.barplot(ax=axes[0, 0], data=category_summary, 
            x="category", y="total_spent", palette="Blues_d")
axes[0, 0].set_title("Spending by Category")
axes[0, 0].set_xlabel("")
axes[0, 0].set_ylabel("RM")
for i, row in category_summary.iterrows():
    axes[0, 0].text(i, row["total_spent"] + 3, 
                    f"RM{row['total_spent']:.0f}", ha="center", fontsize=9)

# Top Right — Pie chart
axes[0, 1].pie(category_summary["total_spent"],
               labels=category_summary["category"],
               autopct="%1.1f%%",
               colors=sns.color_palette("pastel"))
axes[0, 1].set_title("Spending Breakdown")

# Bottom Left — Income vs Expenses
colors = ["#2ecc71", "#e74c3c", "#3498db"]
axes[1, 0].barh(summary_df["type"], summary_df["amount"], color=colors)
axes[1, 0].set_title("Income vs Expenses")
axes[1, 0].set_xlabel("RM")
for bar, val in zip(axes[1, 0].patches, summary_df["amount"]):
    axes[1, 0].text(bar.get_width() + 10, bar.get_y() + bar.get_height() / 2,
                    f"RM {val:.0f}", va="center", fontsize=9)

# Bottom Right — Timeline
axes[1, 1].plot(expenses_only["date"], expenses_only["amount"].abs(),
                marker="o", color="#e74c3c", linewidth=2)
axes[1, 1].set_title("Expense Timeline")
axes[1, 1].set_xlabel("Date")
axes[1, 1].set_ylabel("RM")

plt.tight_layout()
plt.savefig("chart5_dashboard.png", dpi=150)
plt.show()
print("✅ Full dashboard saved as chart5_dashboard.png")