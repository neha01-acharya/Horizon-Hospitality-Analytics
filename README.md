# 🏨 Horizon Hospitality Analytics

## Project Overview

Horizon Hospitality Analytics is a hotel performance analytics project designed to help hotel management understand operational efficiency, room revenue, guest satisfaction, and workforce performance.

The project uses a MySQL database to store and organise hospitality data and a Python-based Streamlit dashboard to present key business performance indicators, seasonal trends, hotel comparisons, and actionable business insights.

The dashboard enables stakeholders to explore performance across different hotels, reporting years, and seasons.

## Business Objectives

The project aims to help hotel management:

- Monitor room occupancy and room utilisation.
- Evaluate room revenue performance.
- Understand seasonal business trends.
- Track guest satisfaction and feedback.
- Monitor employee attrition and workforce stability.
- Compare performance across hotels.
- Identify areas requiring operational or commercial improvement.

## Key Performance Indicators

| KPI | Definition | Business Purpose |
|---|---|---|
| Room Occupancy | Occupied room-days / Available room-days × 100 | Measures room utilisation |
| Average Revenue per Occupied Room | Room revenue / Occupied room-days | Evaluates average room revenue |
| Revenue per Available Room | Room revenue / Available room-days | Measures room revenue efficiency |
| Guest Satisfaction | Average guest feedback rating | Monitors guest experience |
| Employee Attrition | Employee exits / Average headcount × 100 | Monitors workforce retention |

## Dataset and Database

**Database:** `horizon_hospitality_full`

The project uses nine tables organised into dimension and fact tables.

### Dimension Tables

| Table | Description |
|---|---|
| `dim_hotels` | Hotel details, location and property information |
| `dim_rooms` | Room information and room attributes |
| `dim_guests` | Guest information |
| `dim_employees` | Employee details |
| `dim_date` | Calendar and seasonal information |

### Fact Tables

| Table | Description |
|---|---|
| `fact_bookings` | Booking transactions and booking status |
| `fact_room_daily` | Daily room availability, occupancy and room revenue |
| `fact_guest_feedback` | Guest feedback and ratings |
| `fact_employee_employment` | Employee employment and exit information |

### Data Volume

| Table | Records |
|---|---:|
| `dim_hotels` | 15 |
| `dim_rooms` | 1,500 |
| `dim_guests` | 15,000 |
| `dim_employees` | 450 |
| `dim_date` | 1,827 |
| `fact_bookings` | 497,769 |
| `fact_room_daily` | 2,739,000 |
| `fact_guest_feedback` | 277,765 |
| `fact_employee_employment` | 511 |
| **Total** | **3,533,822** |

All nine tables were loaded and reconciled against their respective source CSV files.

## Data Processing and Analytics

The project includes:

1. Loading hospitality datasets from CSV files.
2. Creating and populating MySQL tables.
3. Establishing relationships between dimension and fact tables.
4. Validating record counts and database constraints.
5. Aggregating hotel performance by year and season.
6. Calculating business KPIs using SQL.
7. Connecting the analytical dataset to a Streamlit dashboard.

### Analytical Summary Table

The dashboard uses the aggregated table:

`agg_seasonal_kpis`

It contains hotel-level seasonal performance indicators, including:

- Room occupancy
- Average revenue per occupied room
- Revenue per available room
- Total room revenue
- Guest satisfaction
- Booking cancellations and no-shows
- Employee exits and attrition

This aggregation allows the dashboard to retrieve analytical results without repeatedly scanning the large underlying fact tables.

## Dashboard Features

The Streamlit dashboard provides:

### 1. Interactive Filters
- Reporting year
- Hotel
- Season

### 2. Performance Overview
Displays five major KPIs:
- Room Occupancy
- Average Revenue per Occupied Room
- Revenue per Available Room
- Guest Satisfaction
- Employee Attrition

### 3. KPI Guide
Provides definitions, calculation formulas, business relevance, interpretation and suggested management actions for each KPI.

### 4. Seasonal Business Performance
Visualises:
- Room occupancy across seasons and years.
- Total room revenue across seasons.
- Room occupancy comparison across hotels.

### 5. Business Insights and Recommendations
Generates observations and recommendations based on the selected reporting filters.

### 6. Detailed Performance Report
Displays hotel-level seasonal metrics and provides CSV export functionality.

## Key Business Observations

Based on the seasonal analysis for 2022–2026:

- **Post-Monsoon:** Highest room occupancy at 49.12%.
- **Winter:** Highest average revenue per occupied room at ₹5,455.58 and highest revenue per available room at ₹2,672.77.
- **Monsoon:** Lowest room occupancy at 48.68%, lowest average revenue per occupied room at ₹4,466.19, and lowest revenue per available room at ₹2,174.13.
- **Guest Satisfaction:** Average rating remains consistent at approximately 4.14/5 across seasons.
- **Employee Attrition:** Highest average attrition is observed during Monsoon at 3.05%.

### Business Recommendations

- Evaluate demand-generation campaigns during weaker occupancy periods.
- Review room pricing and promotional strategies during Monsoon.
- Identify successful Winter pricing practices.
- Monitor guest feedback to maintain service quality.
- Investigate workforce retention and staffing patterns during periods of higher attrition.

*These observations represent seasonal associations and should not be interpreted as proof of causation.*

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and application development |
| MySQL | Database management and storage |
| SQL | Data transformation, aggregation and KPI calculations |
| Pandas | Data manipulation and analysis |
| SQLAlchemy | Database connectivity |
| PyMySQL | MySQL driver |
| Streamlit | Interactive dashboard |
| Plotly Express | Data visualisation |

## Project Structure

```text
Horizon_Hospitality/
│
├── generated_data/
│   └── Source CSV datasets
│
├── python/
│   ├── config.py
│   └── load_data.py
│
├── dashboard/
│   ├── app.py
│   ├── db_connection.py
│   └── queries.py
│
├── requirements.txt
└── README.md
```

## Setup and Execution

### Prerequisites

- Python 3.x
- MySQL Server
- pip
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Horizon_Hospitality
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL

Create the database:

```sql
CREATE DATABASE horizon_hospitality_full;
```

Configure the MySQL connection details in the project configuration.

Use environment variables or a local `.env` file for credentials. Do not commit passwords or other secrets to Git.

### 5. Load the Data

Ensure the source CSV files are available in `generated_data/`.

Run:

```bash
python python/load_data.py
```

### 6. Prepare the Analytical Table

Execute the SQL aggregation script or query used to create `agg_seasonal_kpis` after the source tables have been loaded.

### 7. Launch the Dashboard

From the project root:

```bash
streamlit run dashboard/app.py
```

The dashboard will be available at:

`http://localhost:8501`

## Future Enhancements

- Hotel-level revenue forecasting.
- Demand forecasting and seasonal planning.
- Deeper analysis of booking cancellations.
- Guest feedback sentiment analysis.
- Employee retention trend analysis.
- Additional operational performance indicators.

## Conclusion

Horizon Hospitality Analytics transforms large hospitality datasets into meaningful business insights. By combining relational database design, SQL-based analytics and interactive visualisation, the project provides hotel management with a consolidated view of business performance and supports more informed operational and commercial decisions.