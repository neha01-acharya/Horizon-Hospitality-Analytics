# Requirements Traceability Matrix — Horizon Hospitality

Status meanings:
- **Design defined**: design response documented; not yet implemented.
- **Pending**: implementation and evidence still required.
- **Blocked**: cannot proceed until an external dependency is resolved.

| ID | Assignment requirement | Planned implementation | Evidence required | Status |
|---|---|---|---|---|
| R01 | Create SQL database using supplied reference data model; entities/relationships may be added | MySQL database with hotel, guest, employee and supporting entities | ERD, DDL, table/constraint inspection | Design defined |
| R02 | Generate realistic sample data for 5 years using Python/Pandas | Python scripts generate synthetic data for 2022–2026, UUID identifiers and realistic names | Scripts, generated files, row counts and quality report | Pending |
| R03 | Incorporate supplied trends and variation samples | Implement documented seasonal and operational patterns; distinguish supplied qualitative descriptions from synthetic numerical assumptions | Assumptions register, monthly distributions and trend checks | Pending |
| R04 | After SQL tables are created, write SQL queries to create aggregate tables, potentially multiple, with business joins | Build KPI and analytical aggregate tables from detailed facts | SQL scripts, aggregate table checks and reconciliation report | Pending |
| R05 | Connect aggregate tables to dashboard tool | Power BI connection after approved access route is established | Successful connection and refresh evidence | Blocked |
| R06 | Dashboard must have one panel for each KPI | Five KPI panels: occupancy, ADR, RevPAR, guest satisfaction, employee turnover | Dashboard screenshots and KPI reconciliation | Blocked |
| R07 | Create inference document from dataset explaining stories around variations | Evidence-backed synthetic business interpretation | Inference document with query outputs and caveats | Pending |

## KPI traceability

| KPI | Formula | Source table | Required validation |
|---|---|---|---|
| Occupancy Rate | Occupied sellable room-nights / sellable room-nights × 100 | fact_room_daily | Occupied room-nights never exceed sellable room-nights |
| ADR | Accommodation room revenue / occupied room-nights | fact_room_daily | Reconcile revenue and occupied-night totals |
| RevPAR | Accommodation room revenue / sellable room-nights | fact_room_daily | Reconcile revenue and sellable-night totals |
| Guest Satisfaction | Sum valid ratings / count valid ratings | fact_guest_feedback | Ratings are 1–5; feedback booking and guest match |
| Employee Turnover | Company exits / average daily company headcount × 100 | fact_employee_employment | Transfers excluded; daily headcount reconciled |

The matrix is a living control document. Update statuses only when implementation evidence exists. A design definition is not proof of implementation.
