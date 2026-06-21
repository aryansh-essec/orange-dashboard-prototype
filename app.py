import streamlit as st
import pandas as pd
import plotly.express as px 

# cmd - python3 -m streamlit run app.py

# Brand palette (Orange-inspired)
ORANGE = "#FF7900"
BLACK = "#000000"
DARK_GREY = "#595959"
MID_GREY = "#7A7A7A"
LIGHT_GREY = "#F2F2F2"
PALETTE = ["#FF7900", "#000000", "#595959", "#A6A6A6", "#FFB266"]

def style_chart(fig):
    """Apply consistent Orange-brand styling to a Plotly figure."""
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Helvetica Neue, Arial, sans-serif", color=BLACK, size=13),  # ← Helvetica Neue
        title_font=dict(size=14, color=DARK_GREY),  # ← was size=16, color=BLACK
        xaxis=dict(showgrid=True, gridcolor=LIGHT_GREY, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=LIGHT_GREY, zeroline=False),
        legend=dict(bgcolor="white", bordercolor=LIGHT_GREY, borderwidth=1)
    )
    return fig

st.set_page_config(
    page_title="Orange Dashboard Proposal",
    page_icon="🟠",
    layout="wide"
)

st.markdown("""
<style>
/* Heavier, more confident typography */
html, body, [class*="css"] {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
}
h1 { font-weight: 800 !important; letter-spacing: -0.5px; }
h2 { font-weight: 700 !important; letter-spacing: -0.3px; margin-top: 1.5rem !important; }
h3 { font-weight: 700 !important; }
/* More breathing room around section dividers */
hr { margin-top: 2rem !important; margin-bottom: 2rem !important; }

/* Top accent bar */
[data-testid="stAppViewContainer"] > .main {
    border-top: 6px solid #FF7900;
    padding-top: 1rem;
}
            
/* KPI card styling */
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1.5px solid #FF7900;
    border-radius: 6px;
    padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}

[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 14px rgba(255, 121, 0, 0.18);
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    font-weight: 600 !important;
    color: #595959 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

[data-testid="stMetricValue"] {
    font-weight: 800 !important;
    color: #0F0F0F !important;
    font-size: 1.75rem !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.85rem !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div style="
    background-color: #0F0F0F;
    padding: 60px 48px 60px 48px;
    margin: -6rem -5rem 2.5rem -5rem;
    display: flex;
    align-items: center;
    min-height: 140px;
">
    <h1 style="
        color: #FFFFFF;
        margin: 0;
        padding: 0;
        font-weight: 800;
        font-size: 2.5rem;
        letter-spacing: -0.5px;
        text-align: left;
    ">
        Orange Recharging Operations Dashboard
    </h1>
</div>
""", unsafe_allow_html=True)


df = pd.read_excel("Sample_dashboard_data.xlsx")

# Clean: turn "84%" (text) into 84.0 (a number)
df["Progress Rate"] = df["Progress Rate"].str.replace("%", "").astype(float)

# Clean: turn Year "2023" (a number) into "2023" (text)
df["Year"] = df["Year"].astype(str)

# ============================================================
# FILTERS (in the sidebar)
# ============================================================
st.sidebar.header("Filters")

# Build the lists of options from the data itself, so they always match
year_options = sorted(df["Year"].unique().tolist())
region_options = sorted(df["Region"].unique().tolist())
service_options = sorted(df["Service"].unique().tolist())
bu_options = sorted(df["Business Unit Name"].unique().tolist())
allocation_options = sorted(df["Service Allocation"].unique().tolist())
portfolio_options = sorted(df["Service Portfolio"].unique().tolist())

selected_years = st.sidebar.multiselect(
    "Year", options=year_options, default=year_options
)
selected_regions = st.sidebar.multiselect(
    "Region", options=region_options, default=region_options
)
selected_services = st.sidebar.multiselect(
    "Service", options=service_options, default=service_options
)
selected_bus = st.sidebar.multiselect(
    "Business Unit", options=bu_options, default=bu_options
)
selected_allocations = st.sidebar.multiselect(
    "Service Allocation", options=allocation_options, default=allocation_options
)
selected_portfolios = st.sidebar.multiselect(
    "Service Portfolio", options=portfolio_options, default=portfolio_options
)

# Apply the filters to the dataframe
df = df[
    df["Year"].isin(selected_years)
    & df["Region"].isin(selected_regions)
    & df["Service"].isin(selected_services)
    & df["Business Unit Name"].isin(selected_bus)
    & df["Service Allocation"].isin(selected_allocations)
    & df["Service Portfolio"].isin(selected_portfolios)
]

# Safety: if the user deselects everything, warn and stop
if len(df) == 0:
    st.warning("No data matches your filter selection. Adjust the filters.")
    st.stop()

st.sidebar.caption(f"Showing **{len(df)}** of 100 rows")

# Sections to Filter & Display
st.sidebar.markdown("---")
st.sidebar.subheader("Sections to display")

show_kpis = st.sidebar.checkbox("KPI cards", value=True)
show_regional = st.sidebar.checkbox("Regional performance", value=True)
show_breakdowns = st.sidebar.checkbox("Performance breakdowns", value=True)
show_portfolio = st.sidebar.checkbox("Service Portfolio", value=True)
show_findings = st.sidebar.checkbox("Key findings", value=True)
show_quality = st.sidebar.checkbox("Data quality review", value=True)



# KPIs
if show_kpis:
    st.subheader("Key Performance Indicators")
    st.caption("Headline operational metrics across the filtered view.")

    # KPI 1 — Achievement Rate (actual delivered vs theoretical plan)
    total_actual = df["Total Recharging"].sum()
    total_plan   = df["Total Theoretical Country Recharging (PCR)"].sum()
    achievement_rate = total_actual / total_plan * 100

    # KPI 2 — Billing Efficiency (invoiced vs delivered)
    total_invoiced = df["Invoiced Amount"].sum()
    billing_efficiency = total_invoiced / total_actual * 100

    # KPI 3 — Total Invoiced Amount (the headline money number)
    # already have total_invoiced from above

    # KPI 4 — Provisioning Ratio (reserves held vs delivered work)
    total_provisioned = df["Provisioned Amount"].sum()
    provisioning_ratio = total_provisioned / total_actual * 100

    # KPI 5 — Year-over-Year change in delivered recharging
    yoy = df.groupby("Year")["Total Recharging"].sum()

    if "2023" in yoy.index and "2024" in yoy.index:
        yoy_change = (yoy["2024"] - yoy["2023"]) / yoy["2023"] * 100
        yoy_display = f"{yoy_change:+.1f}%"
        yoy_delta = f"{yoy_change:+.1f}%"
    else:
        yoy_display = "—"
        yoy_delta = None


    # Layout the six KPIs as side-by-side cards
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        label="Achievement Rate",
        value=f"{achievement_rate:.1f}%",
        help="Actual recharging delivered as a share of the theoretical plan."
    )
    col2.metric(
        label="Billing Efficiency",
        value=f"{billing_efficiency:.1f}%",
        help="Invoiced as a share of delivered recharging (assumes same units)."
    )
    col3.metric(
        label="Total Invoiced",
        value=f"{total_invoiced/1_000_000:.1f}M",
        help="Total invoiced amount across the dataset."
    )
    col4.metric(
        label="Provisioning Ratio",
        value=f"{provisioning_ratio:.1f}%",
        help="Reserves held as a share of delivered recharging."
    )
    col5.metric(
        label="YoY Recharging",
        value=yoy_display,
        delta=yoy_delta,
        help="Change in delivered recharging from 2023 to 2024. Requires both years in view."
    )

# CHARTS REGIONAL PERFORMANCE
if show_regional:
    st.markdown("---")
    st.subheader("Regional performance")
    st.caption("Two views of the same data: absolute amounts and gap as a percentage of plan.")

    left, right = st.columns(2, gap="large")

    with left:

        # ---- CHART 1A: Plan vs Actual by Region ----
        #st.subheader("Actual vs Theoretical Plan, by Region")

        # Group the data by Region and sum the relevant columns
        by_region = df.groupby("Region")[
            ["Total Recharging", "Total Theoretical Country Recharging (PCR)"]
        ].sum().reset_index()

        # Rename for cleaner labels
        by_region = by_region.rename(columns={
            "Total Theoretical Country Recharging (PCR)": "Theoretical Plan",
            "Total Recharging": "Actual Delivered"
        })

        # Reshape from wide to long so Plotly can show two bars per region
        by_region_long = by_region.melt(
            id_vars="Region",
            value_vars=["Theoretical Plan", "Actual Delivered"],
            var_name="Type",
            value_name="Amount"
        )

        # Build the chart
        
        fig = px.bar(
            by_region_long,
            x="Region",
            y="Amount",
            color="Type",
            barmode="group",
            title="Expected Value vs Actual Delivered, by Region",
            color_discrete_map={
                "Actual Delivered": ORANGE,
                "Theoretical Plan": MID_GREY
            }
        )
        fig.update_layout(
            xaxis_title="",
            yaxis_title="",
            margin=dict(l=10, r=40, t=60, b=40)
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        # ---- CHART 1b: Under-delivery rate by Region (percentage view) ----
        #st.subheader("Under-delivery rate by Region (% of plan missed)")

        # Compute the gap as a percentage of plan
        by_region["Gap %"] = (
            (by_region["Theoretical Plan"] - by_region["Actual Delivered"])
            / by_region["Theoretical Plan"] * 100
        )

        # Sort so the worst region is at the top of the chart
        by_region_sorted = by_region.sort_values("Gap %", ascending=True)

        fig2 = px.bar(
            by_region_sorted,
            x="Gap %",
            y="Region",
            orientation="h",
            title="Under-delivery rate by Region (% of plan missed)", #Share of expected value not delivered",
            text="Gap %",
            color_discrete_sequence=[ORANGE]
        )
        fig2.update_layout(
            xaxis_title="Under-delivery (%)",
            yaxis_title="",
            margin=dict(l=10, r=80, t=60, b=40),
            xaxis=dict(range=[0, 30], dtick=10)
        )
        # Polish: show the % values on the bars, one decimal
        fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig2.update_layout(xaxis_title="Under-delivery (%)", yaxis_title="")

        st.plotly_chart(fig2, use_container_width=True)


# CHARTS Performance breakdowns
if show_breakdowns:
    st.markdown("---")
    st.subheader("Performance breakdowns")
    st.caption("Performance by Business Unit and year-over-year change by Service.")

    left, right = st.columns(2, gap="large")

    with left:
        # ---- CHART 2A: Achievement Rate by Business Unit ----
        #st.subheader("Achievement Rate by Business Unit")

        # Group by Business Unit, sum the two columns
        by_bu = df.groupby("Business Unit Name")[
            ["Total Recharging", "Total Theoretical Country Recharging (PCR)"]
        ].sum().reset_index()

        # Compute the achievement rate per BU
        by_bu["Achievement Rate"] = (
            by_bu["Total Recharging"]
            / by_bu["Total Theoretical Country Recharging (PCR)"]
            * 100
        )

        # Sort worst first (lowest achievement at the top)
        by_bu = by_bu.sort_values("Achievement Rate", ascending=True)

        fig3 = px.bar(
            by_bu,
            x="Achievement Rate",
            y="Business Unit Name",
            orientation="h",
            title="Achievement Rate by Business Unit",
            text="Achievement Rate",
            color_discrete_sequence=[ORANGE]
        )
        fig3.update_layout(
            xaxis_title="Achievement Rate (%)",
            yaxis_title="",
            margin=dict(l=10, r=80, t=60, b=40),
            xaxis=dict(range=[0, 90])
        )
        fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig3.update_layout(xaxis_title="Achievement Rate (%)", yaxis_title="")

        st.plotly_chart(fig3, use_container_width=True)

    with right:
        # ---- CHART 2B: 2023 vs 2024 by Service ----
        #st.subheader("Year-over-Year delivered recharging, by Service")

        # Group by Year and Service
        by_year_service = df.groupby(["Year", "Service"])["Total Recharging"].sum().reset_index()

        fig4 = px.bar(
            by_year_service,
            x="Service",
            y="Total Recharging",
            color="Year",
            barmode="group",
            title="Delivered recharging, 2023 vs 2024, by Service",
            color_discrete_map={
                "2023": MID_GREY,
                "2024": ORANGE
            }
        )
        fig4.update_layout(yaxis_title="Total Recharging")

        st.plotly_chart(fig4, use_container_width=True)


# CHART 3: 2023 vs 2024 by Service Portfolio
if show_portfolio:
    st.markdown("---")
    st.subheader("Performance by Service Portfolio")
    st.caption("Achievement rate across portfolios. Portfolio meanings to confirm with the team.")

    by_portfolio = df.groupby("Service Portfolio")[
        ["Total Recharging", "Total Theoretical Country Recharging (PCR)"]
    ].sum().reset_index()

    by_portfolio["Achievement Rate"] = (
        by_portfolio["Total Recharging"]
        / by_portfolio["Total Theoretical Country Recharging (PCR)"]
        * 100
    )
    by_portfolio = by_portfolio.sort_values("Achievement Rate", ascending=True)

    fig5 = px.bar(
        by_portfolio,
        x="Achievement Rate",
        y="Service Portfolio",
        orientation="h",
        title="Achievement Rate by Service Portfolio",
        text="Achievement Rate",
        color_discrete_sequence=[ORANGE]
    )
    fig5.update_layout(
        xaxis_title="Achievement Rate (%)",
        yaxis_title="",
        margin=dict(l=10, r=80, t=60, b=40),
        xaxis=dict(range=[0, 90])
    )
    fig5.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig5.update_layout(xaxis_title="Achievement Rate (%)", yaxis_title="")

    st.plotly_chart(fig5, use_container_width=True)

# CHART 4: Key findings
if show_findings:
    st.markdown("---")
    st.subheader("Key findings")

    with st.container(border=True):
        st.markdown(
            """
            - **West Coast** shows the largest gap to plan, in both absolute and percentage terms.
            - **East Coast** looks mid-pack in absolute terms but is among the worst in percentage terms. A conventional chart wouldn't flag it.
            - **Maintenance grew and Repair declined** between 2023 and 2024. Possibly linked, but two years isn't enough to confirm.
            - **Business Units are tightly clustered** within about 5 points. Under-achievement appears structural, not team-specific.
            - **Service Portfolio results** need context. Knowing which portfolio performs well requires understanding what each represents.
            """
        )

# Data quality review — six checks every dataset deserves
if show_quality:
    with st.expander("Data quality review (click to expand)"):
        
        # (1) Shape — how big is the table?
        st.markdown("**1. Shape**")
        st.write(f"Rows: {len(df)}  |  Columns: {len(df.columns)}")

        # (2) Column types — is every column the kind of thing it should be?
        st.markdown("**2. Column types AFTER cleaning (Year & Progress Rate)**")
        st.write(df.dtypes.astype(str))

        # (3) Missing values — any blank cells?
        st.markdown("**3. Missing values per column**")
        st.write(df.isnull().sum())

        # (4) Duplicates — fully identical rows, and business-key duplicates
        st.markdown("**4. Duplicates**")
        full_dupes = df.duplicated().sum()
        key_cols = ["Year", "Service", "Sub-Region Name",
                    "Business Unit Name", "Service Portfolio", "Service Allocation"]
        key_dupes = df.duplicated(subset=key_cols).sum()
        st.write(f"Fully identical rows: {full_dupes}")
        st.write(f"Rows sharing the same category combination: {key_dupes}")

        # (5) Distinct values in each category column
        st.markdown("**5. Distinct values in each category**")
        category_cols = ["Year", "Service", "Region", "Sub-Region Name",
                        "Business Unit Name", "Service Portfolio",
                        "Service Allocation", "Recharging Roadmap"]
        for col in category_cols:
            values = sorted(df[col].astype(str).unique().tolist())
            st.write(f"**{col}** ({len(values)} unique): {values}")

        # (6) Summary statistics for the numeric columns
        st.markdown("**6. Summary statistics (numbers only)**")
        st.dataframe(df.describe().round(1))

        # Cleaned data table
        st.subheader("Cleaned data")
        st.dataframe(df)
