# Horizon Hospitality Group — Design Baseline

## 1. Project purpose

Build a synthetic hospitality analytics solution for a fictional hotel group. The solution will generate data with Python/Pandas, store it in MySQL, calculate business aggregates using SQL, and prepare a Power BI dashboard if an organisation-approved Power BI authoring route becomes available.

All records and business findings are synthetic. They must not be represented as actual hotel operating data.

## 2. Confirmed scope

| Item | Decision |
|---|---|
| Project | Horizon Hospitality Group |
| Cities | Goa, Bengaluru, Chennai, Jaipur, Manali |
| Hotels | 15 (3 per city) |
| Rooms | Approximately 1,500 |
| Analysis period | 2022-01-01 through 2026-12-31 |
| Database | MySQL |
| UUID storage | CHAR(36) |
| Data generation | Python and Pandas |
| Dashboard target | Power BI, subject to organisation access |

The 2022–2026 dataset is synthetic. Since the project is being prepared during November 2026, dates after the generation run date must be explicitly described as simulated future-period records.

## 3. Proposed data model

The design contains nine tables.

### Dimensions
- `dim_hotels`: one row per hotel.
- `dim_rooms`: one row per physical room.
- `dim_guests`: one row per guest.
- `dim_employees`: one row per employee identity.
- `dim_date`: one row per calendar date.

### Facts
- `fact_bookings`: one row per booking; each booking reserves one room.
- `fact_room_daily`: one row per physical room per calendar night.
- `fact_guest_feedback`: one row per feedback submission; at most one submission per booking in this project.
- `fact_employee_employment`: one row per employee employment period at a hotel.

## 4. Relationship rules

- One hotel has many rooms, bookings, room-night records, feedback records and employment periods.
- One guest can make many bookings and submit feedback for completed bookings.
- One room can be associated with many bookings over time.
- One room has at most one `fact_room_daily` row per date.
- One booking can produce multiple room-night records, one per occupied night.
- One employee can have multiple employment periods, allowing hotel transfers.
- A booking is for one room only. Multi-room booking groups are out of scope.
- Checkout date is exclusive: a booking from June 1 to June 3 occupies the nights of June 1 and June 2.

## 5. KPI definitions

### Occupancy Rate
Occupied sellable room-nights / sellable room-nights × 100.

### Average Daily Rate (ADR)
Accommodation room revenue / occupied room-nights.

### Revenue Per Available Room (RevPAR)
Accommodation room revenue / sellable room-nights.

### Guest Satisfaction
Sum of valid guest ratings / count of valid guest ratings. Valid ratings are integers from 1 through 5.

### Employee Turnover
Company exits during the period / average daily company headcount during the period × 100.

Internal transfers between hotels are not company exits. Employment intervals are hire-date inclusive and exit-date exclusive.

## 6. Room-night business rules

- A room is sellable when it is available for sale that night.
- Maintenance/out-of-service rooms are not sellable and cannot be occupied.
- An occupied room-night must reference a valid booking.
- An unoccupied room-night has no booking reference and zero accommodation revenue.
- An occupied room-night can have zero revenue only if a documented complimentary/free-night scenario is intentionally generated.
- Room revenue excludes food, beverage, spa and other non-room revenue.
- Monthly and annual occupancy, ADR and RevPAR must be calculated from summed numerators and denominators, not averages of daily KPI values.

## 7. Date coverage

The analysis window is 2022-01-01 through 2026-12-31 (inclusive). The date dimension should additionally include 2027-01-01 as a boundary date because checkout dates are exclusive and may equal that date. No 2027 room-night records are part of the five-year analysis window.

## 8. Implementation and validation gates

1. Approve this design baseline and data dictionary.
2. Execute MySQL DDL and inspect tables, keys, constraints and indexes.
3. Generate a small synthetic sample before generating the full dataset.
4. Validate identifiers, referential integrity, dates, booking overlaps, room-night consistency, ratings and employment intervals.
5. Load validated data into MySQL.
6. Reconcile SQL aggregates against independent calculations from detailed records.
7. Build dashboard only after an approved Power BI access/connectivity route is confirmed.
8. Write inferences only from validated synthetic results, clearly labelling them as synthetic.

## 9. Known limitations

- The Power BI Service is currently unavailable through the user's organisation. Dashboard implementation is blocked pending an approved access route.
- MySQL `local_infile` is currently disabled. Initial data loading will use Python connector batch inserts unless a later approved alternative is selected.
- Database version and DDL execution have not yet been validated.
- This document is a design baseline, not evidence that the database or data pipeline has been executed.
