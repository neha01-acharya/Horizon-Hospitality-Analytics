
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "generated_data"

TABLES = [
    "dim_hotels",
    "dim_rooms",
    "dim_guests",
    "dim_employees",
    "dim_date",
    "fact_bookings",
    "fact_room_daily",
    "fact_guest_feedback",
    "fact_employee_employment",
]

errors = []
warnings = []


def error(message):
    errors.append(message)


def warning(message):
    warnings.append(message)


def load_table(table_name):
    path = DATA_DIR / f"{table_name}.csv"

    if not path.exists():
        error(f"Missing file: {path.name}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(path)
        print(f"Loaded {table_name}: {len(df):,} rows")
        return df
    except Exception as exc:
        error(f"Could not read {path.name}: {exc}")
        return pd.DataFrame()


def check_columns(df, table, required_columns):
    missing = set(required_columns) - set(df.columns)

    if missing:
        error(f"{table}: missing columns {sorted(missing)}")
        return False

    return True


def check_primary_key(df, table, column):
    if column not in df.columns:
        return

    if df[column].isna().any():
        error(f"{table}: NULL values in primary key {column}")

    duplicates = df[column].duplicated().sum()

    if duplicates:
        error(f"{table}: {duplicates} duplicate values in {column}")


def check_foreign_key(child_df, child_col, parent_df, parent_col, label):
    if child_col not in child_df.columns or parent_col not in parent_df.columns:
        return

    invalid = (
        child_df[child_col].notna()
        & ~child_df[child_col].isin(parent_df[parent_col])
    )

    if invalid.any():
        error(f"{label}: {invalid.sum()} invalid foreign-key values")


def check_not_null(df, table, columns):
    for column in columns:
        if column not in df.columns:
            continue

        count = df[column].isna().sum()

        if count:
            error(f"{table}: {count} NULL values in required column {column}")


def to_bool(series):
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map({
            "true": True,
            "false": False,
            "1": True,
            "0": False,
        })
    )



def parse_dates(df, columns, table, nullable_columns=None):
    nullable_columns = nullable_columns or []

    for column in columns:
        if column not in df.columns:
            continue

        original = df[column].copy()
        converted = pd.to_datetime(original, errors="coerce").dt.date

        # Only flag invalid dates where a value was originally supplied.
        invalid = original.notna() & converted.isna()

        if column not in nullable_columns:
            invalid = invalid | original.isna()

        if invalid.any():
            error(
                f"{table}: invalid or missing dates in {column}"
            )

        df[column] = converted


# --------------------------------------------------
# LOAD CSV FILES
# --------------------------------------------------

print("\n" + "=" * 55)
print("HORIZON HOSPITALITY DATA VALIDATION")
print("=" * 55)

data = {table: load_table(table) for table in TABLES}

hotels = data["dim_hotels"]
rooms = data["dim_rooms"]
guests = data["dim_guests"]
employees = data["dim_employees"]
dates = data["dim_date"]
bookings = data["fact_bookings"]
room_daily = data["fact_room_daily"]
feedback = data["fact_guest_feedback"]
employment = data["fact_employee_employment"]


# --------------------------------------------------
# 1. REQUIRED COLUMNS
# --------------------------------------------------

required = {
    "dim_hotels": [
        "hotel_id", "hotel_name", "city", "state",
        "hotel_type", "star_rating"
    ],
    "dim_rooms": [
        "room_id", "hotel_id", "room_number",
        "room_type", "base_rate"
    ],
    "dim_guests": [
        "guest_id", "guest_name", "age_group", "guest_segment"
    ],
    "dim_employees": [
        "employee_id", "employee_name"
    ],
    "dim_date": [
        "date_id", "year", "month", "month_name",
        "quarter", "day_of_month", "day_of_week",
        "season", "is_weekend"
    ],
    "fact_bookings": [
        "booking_id", "guest_id", "hotel_id", "room_id",
        "booking_date", "check_in_date", "check_out_date",
        "booking_status"
    ],
    "fact_room_daily": [
        "room_daily_id", "room_id", "hotel_id", "date_id",
        "booking_id", "is_sellable", "is_occupied", "room_revenue"
    ],
    "fact_guest_feedback": [
        "feedback_id", "booking_id", "guest_id", "hotel_id",
        "feedback_date", "rating", "comments"
    ],
    "fact_employee_employment": [
        "employment_id", "employee_id", "hotel_id",
        "department", "position", "hire_date",
        "exit_date", "separation_type", "exit_reason"
    ],
}

for table, columns in required.items():
    check_columns(data[table], table, columns)


# --------------------------------------------------
# 2. PRIMARY KEYS AND REQUIRED VALUES
# --------------------------------------------------

primary_keys = {
    "dim_hotels": ("hotel_id", hotels),
    "dim_rooms": ("room_id", rooms),
    "dim_guests": ("guest_id", guests),
    "dim_employees": ("employee_id", employees),
    "dim_date": ("date_id", dates),
    "fact_bookings": ("booking_id", bookings),
    "fact_room_daily": ("room_daily_id", room_daily),
    "fact_guest_feedback": ("feedback_id", feedback),
    "fact_employee_employment": ("employment_id", employment),
}

for table, (column, df) in primary_keys.items():
    check_primary_key(df, table, column)

required_values = {
    "dim_hotels": (hotels, [
        "hotel_id", "hotel_name", "city", "state",
        "hotel_type", "star_rating"
    ]),
    "dim_rooms": (rooms, [
        "room_id", "hotel_id", "room_number",
        "room_type", "base_rate"
    ]),
    "dim_guests": (guests, ["guest_id", "guest_name"]),
    "dim_employees": (employees, ["employee_id", "employee_name"]),
    "dim_date": (dates, [
        "date_id", "year", "month", "month_name",
        "quarter", "day_of_month", "day_of_week",
        "season", "is_weekend"
    ]),
    "fact_bookings": (bookings, [
        "booking_id", "guest_id", "hotel_id", "room_id",
        "booking_date", "check_in_date", "check_out_date",
        "booking_status"
    ]),
    "fact_room_daily": (room_daily, [
        "room_daily_id", "room_id", "hotel_id", "date_id",
        "is_sellable", "is_occupied", "room_revenue"
    ]),
    "fact_guest_feedback": (feedback, [
        "feedback_id", "booking_id", "guest_id", "hotel_id",
        "feedback_date", "rating"
    ]),
    "fact_employee_employment": (employment, [
        "employment_id", "employee_id", "hotel_id",
        "department", "position", "hire_date"
    ]),
}

for table, (df, columns) in required_values.items():
    check_not_null(df, table, columns)


# --------------------------------------------------
# 3. DATE CONVERSION
# --------------------------------------------------

parse_dates(dates, ["date_id"], "dim_date")

parse_dates(
    bookings,
    ["booking_date", "check_in_date", "check_out_date"],
    "fact_bookings"
)

parse_dates(room_daily, ["date_id"], "fact_room_daily")

parse_dates(feedback, ["feedback_date"], "fact_guest_feedback")

parse_dates(
    employment,
    ["hire_date", "exit_date"],
    "fact_employee_employment",
    nullable_columns=["exit_date"]
)


# --------------------------------------------------
# 4. FOREIGN KEY VALIDATION
# --------------------------------------------------

check_foreign_key(
    rooms, "hotel_id", hotels, "hotel_id",
    "dim_rooms.hotel_id"
)

check_foreign_key(
    bookings, "guest_id", guests, "guest_id",
    "fact_bookings.guest_id"
)

check_foreign_key(
    bookings, "hotel_id", hotels, "hotel_id",
    "fact_bookings.hotel_id"
)

check_foreign_key(
    bookings, "room_id", rooms, "room_id",
    "fact_bookings.room_id"
)

check_foreign_key(
    bookings, "booking_date", dates, "date_id",
    "fact_bookings.booking_date"
)

check_foreign_key(
    bookings, "check_in_date", dates, "date_id",
    "fact_bookings.check_in_date"
)

check_foreign_key(
    bookings, "check_out_date", dates, "date_id",
    "fact_bookings.check_out_date"
)

check_foreign_key(
    room_daily, "room_id", rooms, "room_id",
    "fact_room_daily.room_id"
)

check_foreign_key(
    room_daily, "hotel_id", hotels, "hotel_id",
    "fact_room_daily.hotel_id"
)

check_foreign_key(
    room_daily, "date_id", dates, "date_id",
    "fact_room_daily.date_id"
)

check_foreign_key(
    room_daily, "booking_id", bookings, "booking_id",
    "fact_room_daily.booking_id"
)

check_foreign_key(
    feedback, "booking_id", bookings, "booking_id",
    "fact_guest_feedback.booking_id"
)

check_foreign_key(
    feedback, "guest_id", guests, "guest_id",
    "fact_guest_feedback.guest_id"
)

check_foreign_key(
    feedback, "hotel_id", hotels, "hotel_id",
    "fact_guest_feedback.hotel_id"
)

check_foreign_key(
    feedback, "feedback_date", dates, "date_id",
    "fact_guest_feedback.feedback_date"
)

check_foreign_key(
    employment, "employee_id", employees, "employee_id",
    "fact_employee_employment.employee_id"
)

check_foreign_key(
    employment, "hotel_id", hotels, "hotel_id",
    "fact_employee_employment.hotel_id"
)

check_foreign_key(
    employment, "hire_date", dates, "date_id",
    "fact_employee_employment.hire_date"
)

check_foreign_key(
    employment, "exit_date", dates, "date_id",
    "fact_employee_employment.exit_date"
)


# --------------------------------------------------
# 5. HOTEL AND ROOM VALIDATION
# --------------------------------------------------

if "hotel_name" in hotels.columns:
    if hotels["hotel_name"].duplicated().any():
        error("dim_hotels: duplicate hotel names")

if {"hotel_id", "room_number"}.issubset(rooms.columns):
    if rooms.duplicated(["hotel_id", "room_number"]).any():
        error("dim_rooms: duplicate room number within a hotel")

if "star_rating" in hotels.columns:
    invalid = ~hotels["star_rating"].between(1, 5)
    if invalid.any():
        error("dim_hotels: star_rating outside 1–5")

if "base_rate" in rooms.columns:
    if (rooms["base_rate"] < 0).any():
        error("dim_rooms: negative room base rate")

if {"room_id", "hotel_id"}.issubset(rooms.columns):
    room_hotel_map = rooms.set_index("room_id")["hotel_id"]

    if "room_id" in bookings.columns:
        expected_hotel = bookings["room_id"].map(room_hotel_map)
        mismatch = (
            expected_hotel.notna()
            & (expected_hotel != bookings["hotel_id"])
        )

        if mismatch.any():
            error("fact_bookings: room and hotel do not match")


# --------------------------------------------------
# 6. BOOKING VALIDATION
# --------------------------------------------------

valid_statuses = {
    "Confirmed", "Completed", "Cancelled", "No-show"
}

if "booking_status" in bookings.columns:
    invalid = ~bookings["booking_status"].isin(valid_statuses)

    if invalid.any():
        error(f"fact_bookings: {invalid.sum()} invalid booking statuses")

if {"check_in_date", "check_out_date"}.issubset(bookings.columns):
    invalid = bookings["check_out_date"] <= bookings["check_in_date"]

    if invalid.any():
        error("fact_bookings: checkout must be after check-in")

if {
    "room_id", "check_in_date", "check_out_date"
}.issubset(bookings.columns):

    ordered = bookings.sort_values(
        ["room_id", "check_in_date", "check_out_date"]
    )

    for room_id, group in ordered.groupby("room_id"):
        previous_checkout = None

        for row in group.itertuples():
            if (
                previous_checkout is not None
                and row.check_in_date < previous_checkout
            ):
                error(f"Booking overlap detected for room {room_id}")
                break

            previous_checkout = row.check_out_date


# --------------------------------------------------
# 7. ROOM-DAILY VALIDATION
# --------------------------------------------------

if not room_daily.empty:
    room_daily["is_sellable_bool"] = to_bool(room_daily["is_sellable"])
    room_daily["is_occupied_bool"] = to_bool(room_daily["is_occupied"])

    if room_daily[
        ["is_sellable_bool", "is_occupied_bool"]
    ].isna().any().any():
        error("fact_room_daily: invalid boolean values")

    if {"room_id", "date_id"}.issubset(room_daily.columns):
        if room_daily.duplicated(["room_id", "date_id"]).any():
            error("fact_room_daily: duplicate room/date combinations")

    if {"room_id", "hotel_id"}.issubset(room_daily.columns):
        expected_hotel = room_daily["room_id"].map(room_hotel_map)
        mismatch = (
            expected_hotel.notna()
            & (expected_hotel != room_daily["hotel_id"])
        )

        if mismatch.any():
            error("fact_room_daily: room and hotel do not match")

    occupied = room_daily["is_occupied_bool"]
    sellable = room_daily["is_sellable_bool"]

    if (occupied & ~sellable).any():
        error("fact_room_daily: occupied room is not sellable")

    if (room_daily.loc[occupied, "booking_id"].isna()).any():
        error("fact_room_daily: occupied night has no booking_id")

    if (room_daily.loc[~occupied, "booking_id"].notna()).any():
        error("fact_room_daily: unoccupied night has a booking_id")

    revenue = pd.to_numeric(
        room_daily["room_revenue"], errors="coerce"
    )

    if revenue.isna().any() or (revenue < 0).any():
        error("fact_room_daily: invalid or negative room revenue")

    if (revenue.loc[~occupied] != 0).any():
        error("fact_room_daily: unoccupied night has room revenue")

    # Check occupied nights against the corresponding booking.
    booking_lookup = bookings.set_index("booking_id")

    occupied_rows = room_daily.loc[
        occupied & room_daily["booking_id"].notna()
    ]

    for row in occupied_rows.itertuples():
        if row.booking_id not in booking_lookup.index:
            continue

        booking = booking_lookup.loc[row.booking_id]

        if isinstance(booking, pd.DataFrame):
            error(f"Duplicate booking ID found: {row.booking_id}")
            continue

        if booking["room_id"] != row.room_id:
            error(f"Room mismatch for occupied booking {row.booking_id}")

        if booking["hotel_id"] != row.hotel_id:
            error(f"Hotel mismatch for occupied booking {row.booking_id}")

        if not (
            booking["check_in_date"]
            <= row.date_id
            < booking["check_out_date"]
        ):
            error(f"Room-night date outside booking stay: {row.booking_id}")

        if booking["booking_status"] in {"Cancelled", "No-show"}:
            error(f"Cancelled/no-show booking marked occupied: {row.booking_id}")


# --------------------------------------------------
# 8. GUEST FEEDBACK VALIDATION
# --------------------------------------------------

if not feedback.empty:
    if "booking_id" in feedback.columns:
        if feedback["booking_id"].duplicated().any():
            error("fact_guest_feedback: multiple feedback records per booking")

    if "rating" in feedback.columns:
        rating = pd.to_numeric(feedback["rating"], errors="coerce")

        if rating.isna().any() or (~rating.between(1, 5)).any():
            error("fact_guest_feedback: ratings must be between 1 and 5")

    booking_lookup = bookings.set_index("booking_id")

    for row in feedback.itertuples():
        if row.booking_id not in booking_lookup.index:
            continue

        booking = booking_lookup.loc[row.booking_id]

        if isinstance(booking, pd.DataFrame):
            continue

        if booking["booking_status"] != "Completed":
            error(f"Feedback exists for non-completed booking {row.booking_id}")

        if row.guest_id != booking["guest_id"]:
            error(f"Feedback guest does not match booking {row.booking_id}")

        if row.hotel_id != booking["hotel_id"]:
            error(f"Feedback hotel does not match booking {row.booking_id}")

        if row.feedback_date < booking["check_out_date"]:
            error(f"Feedback date is before checkout for {row.booking_id}")


# --------------------------------------------------
# 9. EMPLOYMENT VALIDATION
# --------------------------------------------------

if not employment.empty:
    valid_separation_types = {"company_exit", "internal_transfer"}

    exited = employment["exit_date"].notna()

    invalid_type = (
        exited
        & ~employment["separation_type"].isin(valid_separation_types)
    )

    if invalid_type.any():
        error("fact_employee_employment: invalid separation_type")

    invalid_dates = (
        exited
        & (
            employment["exit_date"]
            <= employment["hire_date"]
        )
    )

    if invalid_dates.any():
        error("fact_employee_employment: exit_date must be after hire_date")

    ordered = employment.sort_values(
        ["employee_id", "hire_date"]
    )

    for employee_id, group in ordered.groupby("employee_id"):
        previous_exit = None

        for row in group.itertuples():
            if (
                previous_exit is None
                and row != next(group.itertuples())
            ):
                pass

            if previous_exit is not None and row.hire_date < previous_exit:
                error(f"Overlapping employment periods for employee {employee_id}")
                break

            previous_exit = row.exit_date


# --------------------------------------------------
# 10. SUMMARY AND RESULT
# --------------------------------------------------

print("\n" + "=" * 55)
print("VALIDATION SUMMARY")
print("=" * 55)

for table in TABLES:
    print(f"{table:<32} {len(data[table]):>10,} rows")

print(f"\nErrors: {len(errors)}")
print(f"Warnings: {len(warnings)}")

for item in warnings:
    print("WARNING:", item)

for item in errors:
    print("ERROR:", item)

if errors:
    print("\nVALIDATION FAILED. Fix the errors before loading MySQL.")
    raise SystemExit(1)

print("\nVALIDATION PASSED!")
print("The sample data is ready for the next validation stage.")
