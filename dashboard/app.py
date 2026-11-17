import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from db_connection import fetch_data
from queries import SEASONAL_KPI_QUERY


st.set_page_config(
    page_title="Horizon | Hospitality Analytics",
    page_icon="🏨",
    layout="wide",
)

st.title("Horizon | Hospitality Performance")
st.caption(
    "Five-year view of room utilisation, room revenue, guest experience "
    "and workforce attrition."
)

# Keep the Streamlit canvas and Plotly chart surfaces visually continuous.
st.markdown(
    """<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #0B0F14;
    }
    [data-testid="stHeader"] { background: rgba(11, 15, 20, 0.96); }
    [data-testid="stMetric"] {
        background: transparent;
        border: 1px solid #27313D;
        border-radius: 10px;
        padding: 12px 14px;
    }
    </style>""",
    unsafe_allow_html=True,
)

SEASON_ORDER = ["Winter", "Summer", "Monsoon", "Post-Monsoon"]
DEFAULT_YEARS = [2022, 2023, 2024, 2025, 2026]


@st.cache_data(ttl=300)
def load_data():
    return fetch_data(SEASONAL_KPI_QUERY)


def validate_columns(data):
    required = {
        "year", "season", "hotel_name", "city", "hotel_type",
        "total_revenue", "occupied_days", "sellable_days",
        "guest_satisfaction", "employee_turnover_rate",
    }
    missing = sorted(required - set(data.columns))
    if missing:
        st.error("Missing columns in agg_seasonal_kpis: " + ", ".join(missing))
        st.stop()


def calculate_grouped(data, dimensions):
    """Recalculate room KPIs from additive room revenue and room-day totals."""
    if data.empty:
        return pd.DataFrame()

    result = (
        data.groupby(dimensions, as_index=False, dropna=False)
        .agg(
            room_revenue=("total_revenue", "sum"),
            occupied_room_days=("occupied_days", "sum"),
            available_room_days=("sellable_days", "sum"),
            guest_satisfaction=("guest_satisfaction", "mean"),
            employee_attrition=("employee_turnover_rate", "mean"),
        )
    )

    result["occupancy"] = (
        result["occupied_room_days"] * 100
        / result["available_room_days"].replace(0, float("nan"))
    )
    result["adr"] = (
        result["room_revenue"]
        / result["occupied_room_days"].replace(0, float("nan"))
    )
    result["revpar"] = (
        result["room_revenue"]
        / result["available_room_days"].replace(0, float("nan"))
    )
    return result


def portfolio_metrics(data):
    revenue = data["total_revenue"].fillna(0).sum()
    occupied = data["occupied_days"].fillna(0).sum()
    available = data["sellable_days"].fillna(0).sum()

    return {
        "occupancy": occupied * 100 / available if available else 0,
        "adr": revenue / occupied if occupied else 0,
        "revpar": revenue / available if available else 0,
        "rating": data["guest_satisfaction"].mean(),
        "attrition": data["employee_turnover_rate"].mean(),
        "revenue": revenue,
    }



# Consistent, professional palette for the dark dashboard.
SEASON_COLORS = {
    "Winter": "#6FA8DC",
    "Summer": "#65B89A",
    "Monsoon": "#A6A6B8",
    "Post-Monsoon": "#E0A458",
}

DASHBOARD_BG = "#0B0F14"
CHART_BG = DASHBOARD_BG
PANEL_BG = DASHBOARD_BG
TEXT_COLOR = "#E8EDF3"
MUTED_TEXT = "#AAB4C0"
GRID_COLOR = "#27313D"


def style_chart(fig, height=360, show_legend=True):
    """Apply the same dark styling to every Plotly chart."""
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=24, r=24, t=64, b=38),
        font=dict(family="Arial, sans-serif", size=12, color=TEXT_COLOR),
        title=dict(
            font=dict(size=17, color=TEXT_COLOR),
            x=0.02,
            xanchor="left",
        ),
        legend=(
            dict(
                title_text="",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11, color=MUTED_TEXT),
                bgcolor="rgba(0,0,0,0)",
            )
            if show_legend
            else dict(visible=False)
        ),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=DASHBOARD_BG,
        hoverlabel=dict(
            bgcolor="#1B2530",
            bordercolor="#344252",
            font_size=12,
            font_family="Arial",
            font_color=TEXT_COLOR,
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=GRID_COLOR,
        tickfont=dict(color=MUTED_TEXT),
        title_font=dict(color=MUTED_TEXT),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID_COLOR,
        zeroline=False,
        linecolor=GRID_COLOR,
        tickfont=dict(color=MUTED_TEXT),
        title_font=dict(color=MUTED_TEXT),
    )
    return fig


def seasonal_trend(data):
    trend = calculate_grouped(data, ["year", "season"])
    if trend.empty:
        return trend

    trend["year_label"] = trend["year"].astype(int).astype(str)
    trend["season"] = pd.Categorical(
        trend["season"], categories=SEASON_ORDER, ordered=True
    )
    return trend.sort_values(["year", "season"])


def add_trend_line(data, metric, title, y_title, suffix="", prefix=""):
    trend = seasonal_trend(data)
    if trend.empty:
        st.info("No data available for this selection.")
        return

    fig = px.line(
        trend,
        x="year_label",
        y=metric,
        color="season",
        markers=True,
        category_orders={"season": SEASON_ORDER},
        color_discrete_map=SEASON_COLORS,
        title=title,
        labels={
            "year_label": "Reporting Year",
            metric: y_title,
            "season": "Season",
        },
    )
    fig.update_traces(
        line=dict(width=2.8),
        marker=dict(size=8, line=dict(width=1.2, color=CHART_BG)),
        hovertemplate=(
            "Year: %{x}<br>Season: %{fullData.name}<br>"
            + y_title + ": " + prefix + "%{y:,.2f}" + suffix
            + "<extra></extra>"
        ),
    )
    if suffix == "%":
        fig.update_yaxes(ticksuffix="%")
    if prefix == "₹":
        fig.update_yaxes(tickprefix="₹", separatethousands=True)

    st.plotly_chart(style_chart(fig), use_container_width=True)


def add_grouped_bar(data, metric, title, y_title, suffix="", prefix=""):
    """Grouped seasonal bars for direct year-to-year comparisons."""
    trend = seasonal_trend(data)
    if trend.empty:
        st.info("No data available for this selection.")
        return

    fig = px.bar(
        trend,
        x="year_label",
        y=metric,
        color="season",
        barmode="group",
        category_orders={"season": SEASON_ORDER},
        color_discrete_map=SEASON_COLORS,
        title=title,
        labels={
            "year_label": "Reporting Year",
            metric: y_title,
            "season": "Season",
        },
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate=(
            "Year: %{x}<br>Season: %{fullData.name}<br>"
            + y_title + ": " + prefix + "%{y:,.2f}" + suffix
            + "<extra></extra>"
        ),
    )
    if suffix == "%":
        fig.update_yaxes(ticksuffix="%")
    if prefix == "₹":
        fig.update_yaxes(tickprefix="₹", separatethousands=True)

    st.plotly_chart(style_chart(fig, height=390), use_container_width=True)


def add_satisfaction_bar(data):
    """
    Compare city-level guest ratings on the full 0–5 scale.
    The source ratings are tightly clustered, so the full scale is retained
    to avoid exaggerating small differences.
    """
    chart_data = (
        data.dropna(subset=["guest_satisfaction"])
        .groupby("city", as_index=False)
        .agg(guest_satisfaction=("guest_satisfaction", "mean"))
        .sort_values("guest_satisfaction", ascending=True)
    )
    if chart_data.empty:
        st.info("No guest satisfaction data available for this selection.")
        return

    fig = px.bar(
        chart_data,
        x="guest_satisfaction",
        y="city",
        orientation="h",
        title="Average Guest Satisfaction by City",
        labels={
            "guest_satisfaction": "Average guest rating (/5)",
            "city": "City",
        },
        color_discrete_sequence=["#65B89A"],
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="City: %{y}<br>Average rating: %{x:.2f}/5<extra></extra>",
    )
    fig.update_xaxes(range=[0, 5], dtick=1, ticksuffix=" / 5")
    fig.update_layout(showlegend=False)
    st.plotly_chart(
        style_chart(
            fig,
            height=max(330, 58 * len(chart_data)),
            show_legend=False,
        ),
        use_container_width=True,
    )


def add_attrition_bar(data):
    """Grouped bars make seasonal attrition differences easy to compare."""
    add_grouped_bar(
        data,
        "employee_attrition",
        "Employee Attrition by Year and Season",
        "Attrition rate",
        suffix="%",
    )


def seasonal_insight(data, metric, label, formatter, high_is_good=True):
    """Short, filter-aware observation comparing seasonal averages."""
    summary = seasonal_trend(data)
    if summary.empty or metric not in summary:
        return "Not enough data in the current selection to identify a pattern."
    summary = summary.groupby("season", observed=True)[metric].mean().dropna()
    if summary.empty:
        return "Not enough data in the current selection to identify a pattern."
    best = summary.idxmax() if high_is_good else summary.idxmin()
    low = summary.idxmin() if high_is_good else summary.idxmax()
    if best == low:
        return f"{label} is consistent across the selected seasons."
    return (
        f"{best} records the strongest {label.lower()} "
        f"({formatter(summary[best])}); {low} is lowest "
        f"({formatter(summary[low])}) in the selected period."
    )


def satisfaction_insight(data):
    city = (data.dropna(subset=["guest_satisfaction"])
            .groupby("city")["guest_satisfaction"].mean().dropna())
    if city.empty:
        return "No guest feedback is available for the current selection."
    spread = city.max() - city.min()
    if len(city) == 1 or spread < 0.03:
        return "Guest ratings are very similar across the selected cities."
    return (
        f"{city.idxmax()} has the highest average rating "
        f"({city.max():.2f}/5); {city.idxmin()} is lowest "
        f"({city.min():.2f}/5)."
    )


try:
    df = load_data()

    if df.empty:
        st.warning("No data available.")
        st.stop()

    validate_columns(df)

    for col in [
        "year", "total_revenue", "occupied_days", "sellable_days",
        "guest_satisfaction", "employee_turnover_rate",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["year"] = df["year"].astype("Int64")
    df["season"] = df["season"].astype(str)
    for col in ["city", "hotel_type", "hotel_name"]:
        df[col] = df[col].fillna("Unknown").astype(str)

    # --------------------------------------------------------
    # SIDEBAR FILTERS
    # --------------------------------------------------------

    st.sidebar.header("Filters")

    year_options = sorted(int(y) for y in df["year"].dropna().unique())
    default_years = [y for y in DEFAULT_YEARS if y in year_options]
    if not default_years:
        default_years = year_options

    selected_years = st.sidebar.multiselect(
        "Year", year_options, default=default_years
    )

    city_options = sorted(df["city"].unique())
    selected_cities = st.sidebar.multiselect(
        "City", city_options, default=city_options
    )

    city_data = df[df["city"].isin(selected_cities)]
    type_options = sorted(city_data["hotel_type"].unique())
    selected_types = st.sidebar.multiselect(
        "Hotel Type", type_options, default=type_options
    )

    type_data = city_data[city_data["hotel_type"].isin(selected_types)]
    hotel_options = sorted(type_data["hotel_name"].unique())
    selected_hotels = st.sidebar.multiselect(
        "Hotel", hotel_options, default=hotel_options
    )

    season_options = [s for s in SEASON_ORDER if s in df["season"].unique()]
    season_options += sorted(set(df["season"].unique()) - set(season_options))
    selected_seasons = st.sidebar.multiselect(
        "Season", season_options, default=season_options
    )

    if not selected_years or not selected_cities or not selected_types \
            or not selected_hotels or not selected_seasons:
        st.warning("Please select at least one value in each filter.")
        st.stop()

    filtered = df[
        df["year"].isin(selected_years)
        & df["city"].isin(selected_cities)
        & df["hotel_type"].isin(selected_types)
        & df["hotel_name"].isin(selected_hotels)
        & df["season"].isin(selected_seasons)
    ].copy()

    if filtered.empty:
        st.warning("No records match the selected filters.")
        st.stop()

    m = portfolio_metrics(filtered)

    # --------------------------------------------------------
    # 1. EXECUTIVE OVERVIEW
    # --------------------------------------------------------

    st.subheader("Executive Overview")

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Room Occupancy", f"{m['occupancy']:.2f}%")
    k1.caption("Share of available room-days occupied.")
    k2.metric("ADR", f"₹{m['adr']:,.2f}")
    k2.caption("Room revenue per occupied room-day.")
    k3.metric("RevPAR", f"₹{m['revpar']:,.2f}")
    k3.caption("Room revenue per available room-day.")
    k4.metric(
        "Guest Satisfaction",
        f"{m['rating']:.2f}/5" if pd.notna(m["rating"]) else "N/A",
    )
    k4.caption("Average rating from guest feedback.")
    k5.metric(
        "Employee Attrition",
        f"{m['attrition']:.2f}%" if pd.notna(m["attrition"]) else "N/A",
    )
    k5.caption("Employee exits as a share of average headcount.")

    st.caption(
        f"Selected portfolio: **{len(selected_hotels)} hotels** across "
        f"**{len(selected_cities)} cities** | Reporting years: "
        f"**{', '.join(map(str, sorted(selected_years)))}** | "
        f"Room revenue: **₹{m['revenue']:,.0f}**"
    )

    st.divider()

    # --------------------------------------------------------
    # 2–6. KPI ANALYSIS: ONE CHART PER KPI
    # --------------------------------------------------------

    st.subheader("Performance Trends")
    st.caption(
        "Seasonal trends across the selected reporting years. "
        "A consistent dark visual theme is used throughout."
    )

    st.markdown("#### Room Occupancy")
    st.caption("Occupied room-days as a percentage of available room-days.")
    add_trend_line(
        filtered, "occupancy", "Occupancy by Year and Season",
        "Occupancy", suffix="%"
    )
    st.caption("**Insight:** " + seasonal_insight(
        filtered, "occupancy", "occupancy", lambda v: f"{v:.1f}%"
    ))

    st.markdown("#### Average Daily Rate (ADR)")
    st.caption("Room revenue earned per occupied room-day.")
    add_grouped_bar(
        filtered, "adr", "Average Daily Rate by Year and Season",
        "ADR", prefix="₹"
    )
    st.caption("**Insight:** " + seasonal_insight(
        filtered, "adr", "ADR", lambda v: f"₹{v:,.0f}"
    ))

    st.markdown("#### Revenue per Available Room (RevPAR)")
    st.caption("Room revenue earned per available room-day.")
    add_trend_line(
        filtered, "revpar", "RevPAR by Year and Season",
        "RevPAR", prefix="₹"
    )
    st.caption("**Insight:** " + seasonal_insight(
        filtered, "revpar", "RevPAR", lambda v: f"₹{v:,.0f}"
    ))

    st.markdown("#### Guest Satisfaction")
    st.caption(
        "City-wise average feedback rating. Ratings are tightly clustered, "
        "so the chart keeps the honest 0–5 scale rather than magnifying small differences."
    )
    add_satisfaction_bar(filtered)
    st.caption("**Insight:** " + satisfaction_insight(filtered))

    st.markdown("#### Employee Attrition")
    st.caption("Employee exits as a percentage of average employee headcount.")
    add_attrition_bar(filtered)
    st.caption("**Insight:** " + seasonal_insight(
        filtered, "employee_attrition", "attrition", lambda v: f"{v:.2f}%",
        high_is_good=False,
    ))

    st.divider()

    # --------------------------------------------------------
    # 7. CITY AND HOTEL COMPARISON
    # --------------------------------------------------------

    st.subheader("City & Hotel Comparison")

    city_table = calculate_grouped(filtered, ["city"])
    city_table = city_table.rename(
        columns={
            "city": "City",
            "room_revenue": "Room Revenue (₹)",
            "occupancy": "Occupancy (%)",
            "adr": "ADR (₹)",
            "revpar": "RevPAR (₹)",
            "guest_satisfaction": "Guest Rating (/5)",
            "employee_attrition": "Employee Attrition (%)",
        }
    )

    st.markdown("**City performance**")
    st.dataframe(
        city_table[
            [
                "City", "Room Revenue (₹)", "Occupancy (%)", "ADR (₹)",
                "RevPAR (₹)", "Guest Rating (/5)", "Employee Attrition (%)",
            ]
        ].round(2),
        use_container_width=True,
        hide_index=True,
    )

    hotel_table = calculate_grouped(
        filtered, ["hotel_name", "city", "hotel_type"]
    )
    hotel_table = hotel_table.rename(
        columns={
            "hotel_name": "Hotel",
            "city": "City",
            "hotel_type": "Hotel Type",
            "room_revenue": "Room Revenue (₹)",
            "occupancy": "Occupancy (%)",
            "adr": "ADR (₹)",
            "revpar": "RevPAR (₹)",
            "guest_satisfaction": "Guest Rating (/5)",
            "employee_attrition": "Employee Attrition (%)",
        }
    )

    with st.expander("View hotel-level comparison"):
        st.dataframe(
            hotel_table.sort_values("RevPAR (₹)", ascending=False).round(2),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # --------------------------------------------------------
    # 8. DETAILED DATA AND EXPORT
    # --------------------------------------------------------

    st.subheader("Detailed Data")
    st.caption("Hotel-season records included in the current filter selection.")

    display_df = filtered.sort_values(
        ["year", "season", "city", "hotel_name"]
    ).copy()

    display_df = display_df.rename(
        columns={
            "hotel_name": "Hotel",
            "city": "City",
            "hotel_type": "Hotel Type",
            "year": "Reporting Year",
            "season": "Season",
            "sellable_days": "Available Room-Days",
            "occupied_days": "Occupied Room-Days",
            "occupancy_rate": "Room Occupancy (%)",
            "ADR": "ADR (₹)",
            "RevPAR": "RevPAR (₹)",
            "total_revenue": "Room Revenue (₹)",
            "guest_satisfaction": "Guest Satisfaction (/5)",
            "total_bookings": "Total Bookings",
            "cancelled_bookings": "Cancelled Bookings",
            "no_show_bookings": "No-Show Bookings",
            "employee_exits": "Employee Exits",
            "avg_headcount": "Average Employee Headcount",
            "employee_turnover_rate": "Employee Attrition (%)",
        }
    )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.download_button(
        "Download filtered report (CSV)",
        data=display_df.to_csv(index=False).encode("utf-8"),
        file_name="horizon_hospitality_filtered_report.csv",
        mime="text/csv",
    )

    with st.expander("KPI definitions & methodology"):
        st.markdown(
            """
            - **Occupancy:** Occupied Room-Days / Available Room-Days × 100
            - **ADR:** Room Revenue / Occupied Room-Days
            - **RevPAR:** Room Revenue / Available Room-Days
            - **Guest Satisfaction:** Average guest feedback rating
            - **Employee Attrition:** Employee Exits / Average Employee Headcount × 100
            """
        )
        st.caption(
            "Room revenue is room-only revenue, not total hotel revenue. "
            "Room KPIs are recalculated from summed revenue and room-days. "
            "Guest satisfaction and employee attrition remain averages of "
            "hotel-season aggregate values and are not weighted by review "
            "volume or employee headcount. 2027 is excluded from the default "
            "selection because it is a partial year."
        )

except Exception as exc:
    st.error(f"Dashboard could not be loaded: {exc}")
    st.exception(exc)
