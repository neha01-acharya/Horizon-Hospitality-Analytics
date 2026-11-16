# Horizon Hospitality — Data Dictionary (Design Baseline)

Types below are proposed MySQL types. Final DDL must be checked against the installed MySQL version before execution.

| Table | Column | Proposed type | Key / nullability | Meaning |
|---|---|---|---|---|
| dim_hotels | hotel_id | CHAR(36) | PK, NOT NULL | UUID for hotel |
| dim_hotels | hotel_name | VARCHAR(150) | UNIQUE, NOT NULL | Fictional hotel name |
| dim_hotels | city | VARCHAR(50) | NOT NULL | One of the five project cities |
| dim_hotels | state | VARCHAR(50) | NOT NULL | Indian state/territory |
| dim_hotels | hotel_type | VARCHAR(50) | NOT NULL | Hotel category |
| dim_hotels | star_rating | DECIMAL(2,1) | NOT NULL | Synthetic rating from 1 to 5 |
| dim_rooms | room_id | CHAR(36) | PK, NOT NULL | UUID for physical room |
| dim_rooms | hotel_id | CHAR(36) | FK, NOT NULL | Owning hotel |
| dim_rooms | room_number | VARCHAR(20) | NOT NULL | Room identifier within hotel |
| dim_rooms | room_type | VARCHAR(50) | NOT NULL | Room category |
| dim_rooms | base_rate | DECIMAL(10,2) | NOT NULL | Reference nightly rate |
| dim_guests | guest_id | CHAR(36) | PK, NOT NULL | UUID for guest |
| dim_guests | guest_name | VARCHAR(150) | NOT NULL | Synthetic guest name |
| dim_guests | age_group | VARCHAR(30) | NULL | Broad synthetic age band |
| dim_guests | guest_segment | VARCHAR(50) | NULL | Synthetic guest segment |
| dim_employees | employee_id | CHAR(36) | PK, NOT NULL | UUID for employee identity |
| dim_employees | employee_name | VARCHAR(150) | NOT NULL | Synthetic employee name |
| dim_date | date_id | DATE | PK, NOT NULL | Calendar date |
| dim_date | year | SMALLINT | NOT NULL | Calendar year |
| dim_date | month | TINYINT | NOT NULL | Month number |
| dim_date | month_name | VARCHAR(15) | NOT NULL | Month label |
| dim_date | quarter | TINYINT | NOT NULL | Calendar quarter |
| dim_date | day_of_month | TINYINT | NOT NULL | Day number |
| dim_date | day_of_week | VARCHAR(15) | NOT NULL | Weekday label |
| dim_date | season | VARCHAR(30) | NOT NULL | Documented synthetic season classification |
| dim_date | is_weekend | BOOLEAN | NOT NULL | Weekend indicator |
| fact_bookings | booking_id | CHAR(36) | PK, NOT NULL | UUID for booking |
| fact_bookings | guest_id | CHAR(36) | FK, NOT NULL | Booking guest |
| fact_bookings | hotel_id | CHAR(36) | FK, NOT NULL | Booked hotel |
| fact_bookings | room_id | CHAR(36) | FK, NOT NULL | Booked room |
| fact_bookings | booking_date | DATE | FK, NOT NULL | Date booking was made |
| fact_bookings | check_in_date | DATE | FK, NOT NULL | First occupied night |
| fact_bookings | check_out_date | DATE | FK, NOT NULL | Exclusive checkout date |
| fact_bookings | booking_status | VARCHAR(20) | NOT NULL | Confirmed, Completed, Cancelled or No-show |
| fact_room_daily | room_daily_id | CHAR(36) | PK, NOT NULL | UUID for room-night record |
| fact_room_daily | room_id | CHAR(36) | FK, NOT NULL | Physical room |
| fact_room_daily | hotel_id | CHAR(36) | FK, NOT NULL | Hotel for that room-night |
| fact_room_daily | date_id | DATE | FK, NOT NULL | Night represented |
| fact_room_daily | booking_id | CHAR(36) | FK, NULL | Booking if occupied |
| fact_room_daily | is_sellable | BOOLEAN | NOT NULL | Whether room was available for sale |
| fact_room_daily | is_occupied | BOOLEAN | NOT NULL | Whether room was occupied |
| fact_room_daily | room_revenue | DECIMAL(10,2) | NOT NULL | Accommodation revenue for that night |
| fact_guest_feedback | feedback_id | CHAR(36) | PK, NOT NULL | UUID for feedback |
| fact_guest_feedback | booking_id | CHAR(36) | FK, UNIQUE, NOT NULL | Booking being reviewed |
| fact_guest_feedback | guest_id | CHAR(36) | FK, NOT NULL | Reviewing guest |
| fact_guest_feedback | hotel_id | CHAR(36) | FK, NOT NULL | Reviewed hotel |
| fact_guest_feedback | feedback_date | DATE | FK, NOT NULL | Feedback submission date |
| fact_guest_feedback | rating | TINYINT | NOT NULL | Rating from 1 to 5 |
| fact_guest_feedback | comments | TEXT | NULL | Synthetic feedback text |
| fact_employee_employment | employment_id | CHAR(36) | PK, NOT NULL | UUID for employment period |
| fact_employee_employment | employee_id | CHAR(36) | FK, NOT NULL | Employee identity |
| fact_employee_employment | hotel_id | CHAR(36) | FK, NOT NULL | Hotel for this employment period |
| fact_employee_employment | department | VARCHAR(80) | NOT NULL | Department during this period |
| fact_employee_employment | position | VARCHAR(100) | NOT NULL | Role during this period |
| fact_employee_employment | hire_date | DATE | FK, NOT NULL | First employed date (inclusive) |
| fact_employee_employment | exit_date | DATE | FK, NULL | Last employment boundary (exclusive) |
| fact_employee_employment | separation_type | VARCHAR(30) | NULL | company_exit or internal_transfer |
| fact_employee_employment | exit_reason | VARCHAR(100) | NULL | Synthetic reason, where applicable |

## Design notes

- UUID primary keys are stored as `CHAR(36)` for readability and easier inspection.
- `fact_room_daily` has a unique constraint on `(room_id, date_id)`.
- `fact_bookings` uses one room per booking.
- `fact_guest_feedback` permits at most one feedback submission per booking.
- Employment history is stored separately from employee identity so that position, department and hotel can change over time.
- Some business rules, such as non-overlapping bookings and feedback only after completed stays, require validation queries or generation-time checks; foreign keys alone do not enforce them.
