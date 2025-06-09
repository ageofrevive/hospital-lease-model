import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy_financial as npf
import numpy as np

st.set_page_config(page_title="Hospital Lease Model", layout="centered")

st.title("🏥 Hospital Lease Financial Model")
st.markdown("Use the sliders to explore rent structures based on CapEx, MG, Revenue Share, and growth.")

# --- User Inputs ---
capex = st.number_input("CapEx Investment (₹ Cr)", value=100.0, step=1.0) * 1e7
starting_yield = st.slider("MG Yield (%)", 5.0, 30.0, 20.0, 0.5) / 100
annual_escalation = st.slider("Annual Escalation (%)", 0.0, 10.0, 5.0, 0.5) / 100
revenue_growth = st.slider("Annual Revenue Growth (%)", 0.0, 20.0, 8.0, 0.5) / 100
revenue_share_percent = st.slider("Revenue Share (%)", 1.0, 10.0, 6.0, 0.5) / 100
starting_revenue = st.number_input("Year 1 Revenue (₹ Cr)", value=120.0, step=1.0) * 1e7
years = st.slider("Lease Term (Years)", 5, 30, 15)

# --- Calculations ---
mg_rent = [capex * starting_yield * ((1 + annual_escalation) ** i) for i in range(years)]
revenues = [starting_revenue * ((1 + revenue_growth) ** i) for i in range(years)]
revenue_shares = [rev * revenue_share_percent for rev in revenues]
actual_rent = [max(mg, share) for mg, share in zip(mg_rent, revenue_shares)]

# --- IRR, NPV, Break-even ---
cash_flows = [-capex] + actual_rent
irr = npf.irr(cash_flows)
npv = npf.npv(0.12, cash_flows)
break_even_year = next((i + 1 for i, v in enumerate(np.cumsum(actual_rent)) if v > capex), "Beyond Term")

# --- Table Data ---
df = pd.DataFrame({
    "Year": list(range(1, years + 1)),
    "MG Rent (₹ Cr)": [round(r / 1e7, 2) for r in mg_rent],
    "Hospital Revenue (₹ Cr)": [round(r / 1e7, 2) for r in revenues],
    "Revenue Share (₹ Cr)": [round(r / 1e7, 2) for r in revenue_shares],
    "Final Rent Paid (₹ Cr)": [round(r / 1e7, 2) for r in actual_rent],
})

# --- Display IRR Summary ---
st.subheader("📈 Key Financial Metrics")
st.markdown(f"""
- **IRR**: `{round(irr * 100, 2)}%`
- **NPV (at 12% Discount Rate)**: `₹{round(npv / 1e7, 2)} Cr`
- **Total Rent Collected (15 years)**: `₹{round(sum(actual_rent) / 1e7, 2)} Cr`
- **Break-even Year (Cumulative Rent > CapEx)**: `{break_even_year}`
""")

# --- Table ---
st.subheader("📊 Year-wise Rent Summary")
st.dataframe(df)

# --- Graph ---
st.subheader("📉 Rent Structure Over Time")
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df["Year"], df["MG Rent (₹ Cr)"], label="MG Rent", marker='o')
ax.plot(df["Year"], df["Revenue Share (₹ Cr)"], label="Revenue Share", marker='s')
ax.plot(df["Year"], df["Final Rent Paid (₹ Cr)"], label="Final Rent", marker='^')
ax.set_xlabel("Year")
ax.set_ylabel("₹ Cr")
ax.set_title("MG vs Revenue Share vs Final Rent")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# --- Download CSV ---
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download CSV", csv, "hospital_lease_model.csv", "text/csv")
