
import streamlit as st
import plotly.express as px
import pandas as pd

from db_connection import fetch_data
from queries import SEASONAL_KPI_QUERY


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Horizon Hospitality Analytics",
    page_icon="🏨",
    layout="wide"
)

st.title("🏨 Hotel Business Performance Dashboard")

st.caption(
    "A consolidated view of hotel operations, room revenue, "
    "guest experience and workforce performance."
)


# ==================================================
# LOAD DATA
# ==================================================

@st.cache_data(ttl=300)
def load_data():
    return fetch_data(SEASONAL_KPI_QUERY)


try:

    df = load_data()

    if df.empty:
        st.warning("No data available.")
        st.stop()


    # ==================================================
    # DASHBOARD FILTERS
    # ==================================================

    st.sidebar.header("Report Filters")

    years = sorted(df["year"].dropna().unique())

    selected_years = st.sidebar.multiselect(
        "Reporting Year",
        years,
        default=years
    )

    hotels = sorted(df["hotel_name"].dropna().unique())

    selected_hotel = st.sidebar.selectbox(
        "Hotel",
        ["All Hotels"] + hotels
    )

    seasons = [
        "Winter",
        "Summer",
        "Monsoon",
        "Post-Monsoon"
    ]

    selected_seasons = st.sidebar.multiselect(
        "Season",
        seasons,
        default=seasons
    )

    st.sidebar.divider()

    st.sidebar.caption(
        "Use these filters to explore performance "
        "for specific hotels, years and seasons."
    )


    # ==================================================
    # APPLY FILTERS
    # ==================================================

    if not selected_years:
        st.warning("Please select at least one reporting year.")
        st.stop()

    if not selected_seasons:
        st.warning("Please select at least one season.")
        st.stop()

    comparison_df = df[
        df["year"].isin(selected_years)
    ].copy()

    if selected_hotel != "All Hotels":
        comparison_df = comparison_df[
            comparison_df["hotel_name"] == selected_hotel
        ]

    filtered = comparison_df[
        comparison_df["season"].isin(selected_seasons)
    ].copy()

    other_seasons = comparison_df[
        ~comparison_df["season"].isin(selected_seasons)
    ].copy()

    if filtered.empty:
        st.warning("No records match the selected filters.")
        st.stop()


    # ==================================================
    # KPI CALCULATION FUNCTION
    # ==================================================

    def calculate_metrics(data):

        revenue = data["total_revenue"].sum()
        occupied = data["occupied_days"].sum()
        sellable = data["sellable_days"].sum()

        return {
            "revenue": revenue,

            "occupancy": (
                occupied * 100 / sellable
                if sellable else 0
            ),

            "average_room_revenue": (
                revenue / occupied
                if occupied else 0
            ),

            "revenue_per_available_room": (
                revenue / sellable
                if sellable else 0
            ),

            "rating": data["guest_satisfaction"].mean(),

            "attrition": data["employee_turnover_rate"].mean()
        }


    def build_seasonal_summary(data):

        rows = []

        for season in seasons:

            season_data = data[
                data["season"] == season
            ]

            if not season_data.empty:

                rows.append({
                    "season": season,
                    **calculate_metrics(season_data)
                })

        return pd.DataFrame(rows)


    selected_metrics = calculate_metrics(filtered)


    # ==================================================
    # REPORT CONTEXT
    # ==================================================

    year_text = ", ".join(
        map(str, sorted(selected_years))
    )

    hotel_text = (
        selected_hotel
        if selected_hotel != "All Hotels"
        else "All Hotels"
    )

    season_text = ", ".join(selected_seasons)

    st.info(
        f"**Report scope:** {hotel_text}  |  "
        f"**Years:** {year_text}  |  "
        f"**Seasons:** {season_text}"
    )


    # ==================================================
    # KEY PERFORMANCE INDICATORS
    # ==================================================

    st.divider()

    st.markdown("## Overall Performance at a Glance")

    st.caption(
        "These indicators summarise room utilisation, "
        "room revenue, guest experience and employee retention."
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Room Occupancy",
        f"{selected_metrics['occupancy']:.2f}%"
    )
    c1.caption(
        "Share of available room-days that were occupied."
    )

    c2.metric(
        "Average Revenue per Occupied Room",
        f"₹{selected_metrics['average_room_revenue']:,.2f}"
    )
    c2.caption(
        "Average room revenue earned for each occupied room-day."
    )

    c3.metric(
        "Revenue per Available Room",
        f"₹{selected_metrics['revenue_per_available_room']:,.2f}"
    )
    c3.caption(
        "Room revenue earned for each available room-day."
    )

    c4.metric(
        "Guest Satisfaction",
        (
            f"{selected_metrics['rating']:.2f}/5"
            if pd.notna(selected_metrics["rating"])
            else "N/A"
        )
    )
    c4.caption(
        "Average rating provided through guest feedback."
    )

    c5.metric(
        "Employee Attrition",
        (
            f"{selected_metrics['attrition']:.2f}%"
            if pd.notna(selected_metrics["attrition"])
            else "N/A"
        )
    )
    c5.caption(
        "Percentage of employees leaving during the period."
    )


    # ==================================================
    # KPI GUIDE
    # ==================================================

    with st.expander("📘 KPI Guide – Definitions, Formulas and Business Use"):

        st.markdown(
            "This guide explains what each performance indicator "
            "measures, why it matters and how hotel management "
            "can interpret it."
        )

        st.markdown("### 1. Room Occupancy")

        st.markdown(
            """
            **What is it?**

            The percentage of available room-days that were occupied
            during the selected reporting period.

            **Formula:**

            Occupancy = (Occupied Room-Days / Available Room-Days) × 100

            **Why is it used?**

            Helps management understand how effectively the hotel
            is using its available room inventory.

            **How to interpret it:**
            - Higher occupancy generally indicates stronger room utilisation.
            - Lower occupancy may indicate weaker demand or unused room capacity.

            **Management action:**

            Review demand patterns, room availability and promotional
            opportunities to improve room utilisation.
            """
        )

        st.divider()

        st.markdown("### 2. Average Revenue per Occupied Room")

        st.markdown(
            """
            **What is it?**

            The average room revenue earned for each occupied room-day.
            This is commonly known in the hotel industry as ADR.

            **Formula:**

            Average Revenue per Occupied Room = Room Revenue / Occupied Room-Days

            **Why is it used?**

            Helps management evaluate room pricing and understand
            how much revenue occupied rooms generate on average.

            **How to interpret it:**
            - Higher values indicate higher average room revenue.
            - Lower values may indicate lower room rates or greater use of discounts.

            **Management action:**

            Review pricing strategies, discount levels, room categories
            and upselling opportunities.
            """
        )

        st.divider()

        st.markdown("### 3. Revenue per Available Room")

        st.markdown(
            """
            **What is it?**

            The average room revenue generated for every available
            room-day, whether the room was occupied or not.
            This is commonly known as RevPAR.

            **Formula:**

            Revenue per Available Room = Room Revenue / Available Room-Days

            **Why is it used?**

            Combines room occupancy and room pricing into one indicator.
            It helps management understand how effectively available
            room capacity generates revenue.

            **How to interpret it:**
            - Higher values generally indicate stronger room revenue performance.
            - Lower values may indicate low occupancy, lower room rates or both.

            **Management action:**

            Review occupancy and room pricing together rather than
            focusing on either measure in isolation.
            """
        )

        st.divider()

        st.markdown("### 4. Guest Satisfaction")

        st.markdown(
            """
            **What is it?**

            The average rating submitted by guests through feedback
            and review records.

            **Formula:**

            Guest Satisfaction = Sum of Guest Ratings / Number of Ratings

            **Why is it used?**

            Helps management monitor the guest experience and identify
            areas where service quality may need attention.

            **How to interpret it:**
            - Higher ratings generally indicate better guest feedback.
            - Lower ratings may highlight dissatisfaction or service issues.

            **Management action:**

            Review guest comments, identify recurring complaints and
            investigate service areas that need improvement.
            """
        )

        st.divider()

        st.markdown("### 5. Employee Attrition")

        st.markdown(
            """
            **What is it?**

            The percentage of employees who left the organisation
            relative to its average workforce during the period.

            **Formula:**

            Employee Attrition = (Employee Exits / Average Headcount) × 100

            **Why is it used?**

            Helps management monitor workforce stability and understand
            employee retention across hotels and seasons.

            **How to interpret it:**
            - Higher attrition indicates more employee exits relative to workforce size.
            - Lower attrition generally indicates greater workforce stability.

            **Management action:**

            Review staffing patterns, employee feedback, recruitment
            needs and retention practices.
            """
        )

        st.divider()

        st.markdown("### Important interpretation notes")

        st.markdown(
            """
            - Revenue indicators in this dashboard relate to room revenue,
              not necessarily total hotel revenue from food, events or other services.
            - Room occupancy is calculated using occupied and available room-days.
            - Average revenue per occupied room and revenue per available room
              are calculated using aggregated room revenue and room-days.
            - Guest satisfaction and employee attrition are displayed as
              averages of the underlying hotel-season records.
            - A high or low KPI is a signal for investigation, not proof
              of the reason behind a business outcome.
            """
        )


    # ==================================================
    # SEASONAL PERFORMANCE TRENDS
    # ==================================================

    st.divider()

    st.markdown("## Seasonal Business Performance")

    st.caption(
        "Explore how room occupancy and room revenue change "
        "across seasons and reporting years."
    )

    season_order = [
        "Winter",
        "Summer",
        "Monsoon",
        "Post-Monsoon"
    ]

    trend = (
        filtered.groupby(
            ["year", "season"],
            as_index=False,
            observed=True
        )
        .agg(
            occupied_room_days=("occupied_days", "sum"),
            available_room_days=("sellable_days", "sum"),
            revenue=("total_revenue", "sum")
        )
    )

    trend["occupancy_rate"] = (
        trend["occupied_room_days"] * 100 /
        trend["available_room_days"].replace(
            0, float("nan")
        )
    )

    trend["season"] = pd.Categorical(
        trend["season"],
        categories=season_order,
        ordered=True
    )

    trend = trend.sort_values(
        ["year", "season"]
    )


    # --------------------------------------------------
    # CHART 1: ROOM OCCUPANCY
    # --------------------------------------------------

    st.markdown("### Room Occupancy Across Seasons")

    st.caption(
        "Shows the percentage of available room-days occupied "
        "in each season. Use this chart to identify periods of "
        "stronger or weaker room utilisation."
    )

    fig1 = px.line(
        trend,
        x="year",
        y="occupancy_rate",
        color="season",
        markers=True,
        title="Room Occupancy by Year and Season",
        labels={
            "year": "Reporting Year",
            "occupancy_rate": "Room Occupancy (%)",
            "season": "Season"
        }
    )

    fig1.update_layout(
        template="plotly_white",
        height=420,
        title_font_size=20,
        legend_title_text="Season",
        xaxis_title="Reporting Year",
        yaxis_title="Room Occupancy (%)",
        hovermode="x unified"
    )

    fig1.update_yaxes(
        ticksuffix="%"
    )

    fig1.update_traces(
        hovertemplate=(
            "Year: %{x}<br>"
            "Room Occupancy: %{y:.2f}%"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )


    # ==================================================
    # REVENUE COMPARISON
    # ==================================================

    revenue_trend = (
        filtered.groupby(
            "season",
            as_index=False,
            observed=True
        )["total_revenue"].sum()
    )

    revenue_trend["revenue_lakhs"] = (
        revenue_trend["total_revenue"] / 100000
    )

    revenue_trend["season"] = pd.Categorical(
        revenue_trend["season"],
        categories=season_order,
        ordered=True
    )

    revenue_trend = revenue_trend.sort_values(
        "season"
    )


    # --------------------------------------------------
    # CHART 2: ROOM REVENUE
    # --------------------------------------------------

    st.markdown("### Room Revenue Across Seasons")

    st.caption(
        "Compares total room revenue generated in each selected season. "
        "Values are displayed in ₹ lakh for easier comparison."
    )

    fig2 = px.bar(
        revenue_trend,
        x="season",
        y="revenue_lakhs",
        title="Total Room Revenue by Season",
        labels={
            "season": "Season",
            "revenue_lakhs": "Room Revenue (₹ lakh)"
        },
        text_auto=".2f"
    )

    fig2.update_layout(
        template="plotly_white",
        height=420,
        title_font_size=20,
        xaxis_title="Season",
        yaxis_title="Room Revenue (₹ lakh)",
        showlegend=False
    )

    fig2.update_traces(
        textposition="outside",
        hovertemplate=(
            "Season: %{x}<br>"
            "Room Revenue: ₹%{customdata:,.2f}"
            "<extra></extra>"
        ),
        customdata=revenue_trend[["total_revenue"]].values
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


    # ==================================================
    # HOTEL-WISE COMPARISON
    # ==================================================

    hotel_data = (
        filtered.groupby(
            "hotel_name",
            as_index=False
        )
        .agg(
            revenue=("total_revenue", "sum"),
            occupied=("occupied_days", "sum"),
            available=("sellable_days", "sum")
        )
    )

    hotel_data["occupancy_rate"] = (
        hotel_data["occupied"] * 100 /
        hotel_data["available"].replace(
            0, float("nan")
        )
    )

    hotel_data = hotel_data.sort_values(
        "occupancy_rate",
        ascending=False
    )


    # --------------------------------------------------
    # CHART 3: HOTEL COMPARISON
    # --------------------------------------------------

    st.markdown("### Room Occupancy Comparison Across Hotels")

    st.caption(
        "Ranks hotels by room occupancy for the selected reporting "
        "period. This helps management identify stronger-performing "
        "properties and hotels that may need attention."
    )

    fig3 = px.bar(
        hotel_data,
        x="hotel_name",
        y="occupancy_rate",
        title="Hotel-wise Room Occupancy",
        labels={
            "hotel_name": "Hotel",
            "occupancy_rate": "Room Occupancy (%)"
        },
        text_auto=".2f"
    )

    fig3.update_layout(
        template="plotly_white",
        height=480,
        title_font_size=20,
        xaxis_title="Hotel",
        yaxis_title="Room Occupancy (%)",
        showlegend=False,
        xaxis_tickangle=-35
    )

    fig3.update_traces(
        textposition="outside",
        hovertemplate=(
            "Hotel: %{x}<br>"
            "Room Occupancy: %{y:.2f}%"
            "<extra></extra>"
        )
    )

    fig3.update_yaxes(
        ticksuffix="%"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )


    # ==================================================
    # BUSINESS INSIGHTS
    # ==================================================

    st.divider()

    st.markdown("## What the Numbers Tell Us")

    st.caption(
        "Business observations and suggested actions based on "
        "the selected hotels, reporting years and seasons."
    )

    insight_col, recommendation_col = st.columns(2)

    recommendations = []

    with insight_col:

        st.markdown("### Key Business Insights")

        if not other_seasons.empty:

            comparison_metrics = calculate_metrics(
                other_seasons
            )

            occupancy_diff = (
                selected_metrics["occupancy"]
                - comparison_metrics["occupancy"]
            )

            average_room_revenue_diff = (
                selected_metrics["average_room_revenue"]
                - comparison_metrics["average_room_revenue"]
            )

            available_room_revenue_diff = (
                selected_metrics["revenue_per_available_room"]
                - comparison_metrics["revenue_per_available_room"]
            )

            rating_diff = (
                selected_metrics["rating"]
                - comparison_metrics["rating"]
            )

            attrition_diff = (
                selected_metrics["attrition"]
                - comparison_metrics["attrition"]
            )

            st.markdown(
                f"""
                - **Room Occupancy:** {selected_metrics['occupancy']:.2f}%
                  ({occupancy_diff:+.2f} percentage points compared
                  with the unselected seasons).

                - **Average Revenue per Occupied Room:**
                  ₹{selected_metrics['average_room_revenue']:,.2f}
                  ({average_room_revenue_diff:+,.2f} compared
                  with the unselected seasons).

                - **Revenue per Available Room:**
                  ₹{selected_metrics['revenue_per_available_room']:,.2f}
                  ({available_room_revenue_diff:+,.2f} compared
                  with the unselected seasons).

                - **Guest Satisfaction:**
                  {
                      f"{selected_metrics['rating']:.2f}/5"
                      if pd.notna(selected_metrics["rating"])
                      else "Not available"
                  }
                  {
                      f"({rating_diff:+.2f} compared with the unselected seasons)"
                      if pd.notna(rating_diff)
                      else ""
                  }.

                - **Employee Attrition:**
                  {
                      f"{selected_metrics['attrition']:.2f}%"
                      if pd.notna(selected_metrics["attrition"])
                      else "Not available"
                  }
                  {
                      f"({attrition_diff:+.2f} percentage points compared with the unselected seasons)"
                      if pd.notna(attrition_diff)
                      else ""
                  }.
                """
            )

        else:

            seasonal_summary = build_seasonal_summary(
                comparison_df
            )

            if not seasonal_summary.empty:

                best_occupancy = seasonal_summary.loc[
                    seasonal_summary["occupancy"].idxmax()
                ]

                best_revenue = seasonal_summary.loc[
                    seasonal_summary["revenue_per_available_room"].idxmax()
                ]

                lowest_revenue = seasonal_summary.loc[
                    seasonal_summary["revenue_per_available_room"].idxmin()
                ]

                highest_attrition = seasonal_summary.loc[
                    seasonal_summary["attrition"].idxmax()
                ]

                st.markdown(
                    f"""
                    - **Highest Room Occupancy:** {best_occupancy['season']}
                      ({best_occupancy['occupancy']:.2f}%).
                    - **Highest Revenue per Available Room:**
                      {best_revenue['season']}
                      (₹{best_revenue['revenue_per_available_room']:,.2f}).
                    - **Lowest Revenue per Available Room:**
                      {lowest_revenue['season']}
                      (₹{lowest_revenue['revenue_per_available_room']:,.2f}).
                    - **Highest Employee Attrition:**
                      {highest_attrition['season']}
                      ({highest_attrition['attrition']:.2f}%).
                    """
                )


    # ==================================================
    # DYNAMIC RECOMMENDATIONS
    # ==================================================

    if not other_seasons.empty:

        comparison_metrics = calculate_metrics(
            other_seasons
        )

        # Room occupancy

        occupancy_diff = (
            selected_metrics["occupancy"]
            - comparison_metrics["occupancy"]
        )

        if occupancy_diff < -1:

            recommendations.append(
                f"Room occupancy is {abs(occupancy_diff):.2f} "
                "percentage points below the unselected seasons. "
                "Evaluate targeted promotions, demand-generation "
                "campaigns and room availability."
            )

        elif occupancy_diff > 1:

            recommendations.append(
                f"Room occupancy is {occupancy_diff:.2f} "
                "percentage points higher than the unselected seasons. "
                "Review room inventory and opportunities to optimise pricing."
            )

        else:

            recommendations.append(
                "Room occupancy is broadly comparable with the "
                "unselected seasons. Continue monitoring demand "
                "and room utilisation."
            )


        # Average revenue per occupied room

        average_room_revenue_diff = (
            selected_metrics["average_room_revenue"]
            - comparison_metrics["average_room_revenue"]
        )

        if average_room_revenue_diff < 0:

            recommendations.append(
                f"Average revenue per occupied room is "
                f"₹{abs(average_room_revenue_diff):,.2f} lower than "
                "the unselected seasons. Review room rates, discounts "
                "and upselling opportunities."
            )

        else:

            recommendations.append(
                f"Average revenue per occupied room is "
                f"₹{average_room_revenue_diff:,.2f} higher than "
                "the unselected seasons. Review which pricing "
                "practices are contributing to this performance."
            )


        # Revenue per available room

        available_room_revenue_diff = (
            selected_metrics["revenue_per_available_room"]
            - comparison_metrics["revenue_per_available_room"]
        )

        if available_room_revenue_diff < 0:

            recommendations.append(
                "Revenue per available room is lower than in the "
                "unselected seasons. Review room occupancy and "
                "pricing together to identify improvement opportunities."
            )

        else:

            recommendations.append(
                "Revenue per available room is higher than in the "
                "unselected seasons. Identify successful demand "
                "and pricing practices that can be sustained."
            )


        # Guest satisfaction

        rating_diff = (
            selected_metrics["rating"]
            - comparison_metrics["rating"]
        )

        if pd.notna(rating_diff):

            if rating_diff < -0.1:

                recommendations.append(
                    "Guest satisfaction is lower than in the "
                    "unselected seasons. Review guest feedback and "
                    "investigate recurring service-quality concerns."
                )

            else:

                recommendations.append(
                    "Guest satisfaction is comparable to or higher "
                    "than in the unselected seasons. Continue "
                    "monitoring guest feedback and service standards."
                )


        # Employee attrition

        attrition_diff = (
            selected_metrics["attrition"]
            - comparison_metrics["attrition"]
        )

        if pd.notna(attrition_diff):

            if attrition_diff > 0.5:

                recommendations.append(
                    "Employee attrition is higher than in the "
                    "unselected seasons. Review workforce planning, "
                    "staffing patterns and employee retention practices."
                )

            else:

                recommendations.append(
                    "Employee attrition is not higher than in the "
                    "unselected seasons. Continue monitoring workforce "
                    "stability and retention."
                )

    else:

        seasonal_summary = build_seasonal_summary(
            comparison_df
        )

        if not seasonal_summary.empty:

            best_revenue = seasonal_summary.loc[
                seasonal_summary["revenue_per_available_room"].idxmax()
            ]

            lowest_revenue = seasonal_summary.loc[
                seasonal_summary["revenue_per_available_room"].idxmin()
            ]

            lowest_occupancy = seasonal_summary.loc[
                seasonal_summary["occupancy"].idxmin()
            ]

            highest_attrition = seasonal_summary.loc[
                seasonal_summary["attrition"].idxmax()
            ]

            recommendations.append(
                f"{best_revenue['season']} has the strongest revenue "
                f"per available room at "
                f"₹{best_revenue['revenue_per_available_room']:,.2f}. "
                "Study its room pricing and demand patterns."
            )

            recommendations.append(
                f"{lowest_revenue['season']} has the lowest revenue "
                f"per available room at "
                f"₹{lowest_revenue['revenue_per_available_room']:,.2f}. "
                "Review room pricing and revenue opportunities."
            )

            recommendations.append(
                f"{lowest_occupancy['season']} has the lowest room "
                f"occupancy at {lowest_occupancy['occupancy']:.2f}%. "
                "Evaluate targeted campaigns to improve room demand."
            )

            recommendations.append(
                f"{highest_attrition['season']} has the highest "
                f"employee attrition at "
                f"{highest_attrition['attrition']:.2f}%. "
                "Review seasonal staffing and retention practices."
            )


    with recommendation_col:

        st.markdown("### Suggested Management Actions")

        for i, recommendation in enumerate(
            recommendations, 1
        ):

            st.markdown(
                f"**{i}.** {recommendation}"
            )


    st.caption(
        "These observations compare selected seasons with "
        "unselected seasons, or identify seasonal highs and lows "
        "when all seasons are selected. Seasonal associations "
        "do not establish causation."
    )


    # ==================================================
    # DETAILED PERFORMANCE TABLE
    # ==================================================

    st.divider()

    st.markdown("## Detailed Hotel Performance")

    st.caption(
        "Explore the underlying performance indicators for each "
        "hotel, reporting year and season."
    )

    display_df = filtered.sort_values(
        ["year", "season", "hotel_name"]
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
            "ADR": "Average Revenue per Occupied Room (₹)",
            "RevPAR": "Revenue per Available Room (₹)",
            "total_revenue": "Total Room Revenue (₹)",
            "guest_satisfaction": "Guest Satisfaction (/5)",
            "total_bookings": "Total Bookings",
            "cancelled_bookings": "Cancelled Bookings",
            "no_show_bookings": "No-Show Bookings",
            "employee_exits": "Employee Exits",
            "avg_headcount": "Average Employee Headcount",
            "employee_turnover_rate": "Employee Attrition (%)"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


    # ==================================================
    # DOWNLOAD REPORT
    # ==================================================

    st.download_button(
        label="📥 Download Hotel Performance Report",
        data=display_df.to_csv(index=False),
        file_name="hotel_business_performance_report.csv",
        mime="text/csv"
    )


    # ==================================================
    # DATA NOTES
    # ==================================================

    with st.expander("ℹ️ About This Report"):

        st.markdown(
            """
            - The dashboard uses aggregated hotel performance data
              prepared from the underlying booking, room, feedback
              and employee records.
            - Room revenue indicators represent room revenue and
              should not be interpreted as total hotel revenue.
            - Occupancy and revenue calculations use room-days
              to account for differences in room availability.
            - Guest satisfaction and employee attrition are shown
              as averages of the underlying hotel-season records.
            - The report should be interpreted within the selected
              reporting period and filters.
            - Seasonal comparisons highlight patterns and areas
              for investigation; they do not prove the causes
              of business performance.
            """
        )


except Exception as e:

    st.error(
        f"Dashboard error: {e}"
    )
