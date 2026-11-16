
import csv
import random
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

MODE = "full"  # Change to "full" only after sample validation

SEED = 42
random.seed(SEED)

RUN_DATE = date.today()

START_DATE = date(2022, 1, 1)
ANALYSIS_END = date(2026, 12, 31)
BOUNDARY_DATE = date(2027, 1, 1)

CITIES = {
    "Goa": "Goa",
    "Bengaluru": "Karnataka",
    "Chennai": "Tamil Nadu",
    "Jaipur": "Rajasthan",
    "Manali": "Himachal Pradesh"
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "generated_data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if MODE == "sample":
    ROOMS_PER_HOTEL = 5
    GUEST_COUNT = 200
    EMPLOYEES_PER_HOTEL = 4
    ROOM_START = START_DATE
    ROOM_END = date(2022, 2, 1)  # Exclusive
else:
    ROOMS_PER_HOTEL = 100
    GUEST_COUNT = 15000
    EMPLOYEES_PER_HOTEL = 30
    ROOM_START = START_DATE
    ROOM_END = BOUNDARY_DATE

# ============================================================
# COMMON HELPERS
# ============================================================

def new_id():
    return str(uuid.uuid4())


def random_date(start, end):
    """Return a random date between start and end, inclusive."""
    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))


def save_dataframe(name, records):
    df = pd.DataFrame(records)
    path = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"Exported {name}: {len(df):,} rows")
    return df


# ============================================================
# 1. HOTEL DIMENSION
# ============================================================

def generate_hotels():
    hotels = []

    hotel_styles = [
        "Grand", "Royal", "Heritage"
    ]

    hotel_types = [
        "Luxury Resort",
        "Business Hotel",
        "Boutique Hotel",
        "Heritage Hotel",
        "Premium Hotel"
    ]

    for city, state in CITIES.items():
        for number in range(1, 4):
            hotels.append({
                "hotel_id": new_id(),
                "hotel_name": (
                    f"{hotel_styles[number - 1]} "
                    f"{city} Hotel {number}"
                ),
                "city": city,
                "state": state,
                "hotel_type": random.choice(hotel_types),
                "star_rating": round(random.uniform(3.0, 5.0), 1)
            })

    return hotels


# ============================================================
# 2. ROOM DIMENSION
# ============================================================

def generate_rooms(hotels):
    rooms = []

    room_types = (
        ["Standard"] * 30
        + ["Deluxe"] * 40
        + ["Suite"] * 20
        + ["Family"] * 10
    )

    base_rates = {
        "Standard": 2500,
        "Deluxe": 4000,
        "Suite": 7000,
        "Family": 5500
    }

    city_multipliers = {
        "Goa": 1.20,
        "Bengaluru": 1.10,
        "Chennai": 1.00,
        "Jaipur": 1.05,
        "Manali": 1.15
    }

    for hotel in hotels:
        if ROOMS_PER_HOTEL == 100:
            hotel_room_types = room_types.copy()
        else:
            hotel_room_types = [
                "Standard", "Standard",
                "Deluxe", "Suite", "Family"
            ]

        random.shuffle(hotel_room_types)

        for number, room_type in enumerate(
            hotel_room_types, start=101
        ):
            rate = (
                base_rates[room_type]
                * city_multipliers[hotel["city"]]
                * random.uniform(0.90, 1.10)
            )

            rooms.append({
                "room_id": new_id(),
                "hotel_id": hotel["hotel_id"],
                "room_number": str(number),
                "room_type": room_type,
                "base_rate": round(rate, 2)
            })

    return rooms


# ============================================================
# 3. GUEST DIMENSION
# ============================================================

def generate_guests():
    first_names = [
        "Aarav", "Aditi", "Arjun", "Ananya", "Rahul",
        "Priya", "Rohan", "Sneha", "Karan", "Meera",
        "Vikram", "Isha", "Aditya", "Neha", "Varun",
        "Pooja", "Kabir", "Diya", "Sanjay", "Riya"
    ]

    last_names = [
        "Sharma", "Patel", "Reddy", "Nair", "Iyer",
        "Gupta", "Mehta", "Rao", "Kapoor", "Menon",
        "Singh", "Das", "Joshi", "Pillai", "Verma"
    ]

    age_groups = [
        "18-25", "26-35", "36-45",
        "46-55", "56+"
    ]

    segments = [
        "Budget", "Regular", "Premium",
        "Business", "Family"
    ]

    guests = []

    for _ in range(GUEST_COUNT):
        guests.append({
            "guest_id": new_id(),
            "guest_name": (
                f"{random.choice(first_names)} "
                f"{random.choice(last_names)}"
            ),
            "age_group": (
                random.choice(age_groups)
                if random.random() > 0.05 else None
            ),
            "guest_segment": random.choice(segments)
        })

    return guests


# ============================================================
# 4. EMPLOYEE DIMENSION
# ============================================================

def generate_employees(hotels):
    employees = []
    employment = []

    first_names = [
        "Amit", "Kavya", "Rahul", "Sneha", "Arun",
        "Divya", "Manish", "Pallavi", "Ravi", "Anjali",
        "Nikhil", "Swati", "Kiran", "Deepa"
    ]

    last_names = [
        "Sharma", "Rao", "Nair", "Patel",
        "Mehta", "Iyer", "Singh", "Reddy"
    ]

    departments = [
        "Front Office", "Housekeeping",
        "Food and Beverage", "Finance",
        "Human Resources", "Maintenance",
        "Sales and Marketing"
    ]

    positions = {
        "Front Office": ["Receptionist", "Front Office Manager"],
        "Housekeeping": ["Room Attendant", "Housekeeping Supervisor"],
        "Food and Beverage": ["Service Associate", "F&B Manager"],
        "Finance": ["Accountant", "Finance Executive"],
        "Human Resources": ["HR Executive", "HR Manager"],
        "Maintenance": ["Technician", "Maintenance Supervisor"],
        "Sales and Marketing": ["Sales Executive", "Sales Manager"]
    }

    max_date = min(RUN_DATE, ANALYSIS_END)

    for hotel in hotels:
        for _ in range(EMPLOYEES_PER_HOTEL):
            employee_id = new_id()

            employees.append({
                "employee_id": employee_id,
                "employee_name": (
                    f"{random.choice(first_names)} "
                    f"{random.choice(last_names)}"
                )
            })

            hire_date = random_date(START_DATE, max_date)
            current_hotel = hotel["hotel_id"]
            current_hire = hire_date
            department = random.choice(departments)

            # Allow up to two internal transfers.
            for transfer_number in range(2):
                can_transfer_after = (
                    current_hire + timedelta(days=180)
                )

                if (
                    random.random() < 0.12
                    and can_transfer_after < max_date
                ):
                    transfer_date = random_date(
                        can_transfer_after, max_date
                    )

                    employment.append({
                        "employment_id": new_id(),
                        "employee_id": employee_id,
                        "hotel_id": current_hotel,
                        "department": department ,
                        "position": random.choice(positions[department]),
                        "hire_date": current_hire,
                        "exit_date": transfer_date,
                        "separation_type": "internal_transfer",
                        "exit_reason": None
                    })

                    other_hotels = [
                        h for h in hotels
                        if h["hotel_id"] != current_hotel
                    ]

                    current_hotel = random.choice(
                        other_hotels
                    )["hotel_id"]

                    current_hire = transfer_date

                else:
                    break

            # Decide whether the final employment period ends.
            possible_exit = current_hire + timedelta(days=90)

            if (
                random.random() < 0.12
                and possible_exit < max_date
            ):
                exit_date = random_date(possible_exit, max_date)
                separation_type = "company_exit"
                exit_reason = random.choice([
                    "Resignation",
                    "Career Change",
                    "Personal Reasons",
                    "Relocation"
                ])
            else:
                exit_date = None
                separation_type = None
                exit_reason = None

            employment.append({
                "employment_id": new_id(),
                "employee_id": employee_id,
                "hotel_id": current_hotel,
                "department": department,
                "position": random.choice(positions[department]),
                "hire_date": current_hire,
                "exit_date": exit_date,
                "separation_type": separation_type,
                "exit_reason": exit_reason
            })

    return employees, employment


# ============================================================
# 5. DATE DIMENSION
# ============================================================

def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Summer"
    elif month in [6, 7, 8, 9]:
        return "Monsoon"
    else:
        return "Post-Monsoon"


def generate_dates():
    records = []

    current = START_DATE

    while current <= BOUNDARY_DATE:
        records.append({
            "date_id": current,
            "year": current.year,
            "month": current.month,
            "month_name": current.strftime("%B"),
            "quarter": (current.month - 1) // 3 + 1,
            "day_of_month": current.day,
            "day_of_week": current.strftime("%A"),
            "season": get_season(current.month),
            "is_weekend": current.weekday() >= 5
        })

        current += timedelta(days=1)

    return records


# ============================================================
# 6. BOOKINGS
# ============================================================

def generate_bookings(rooms, hotels, guests):
    bookings = []
    room_schedules = {}

    hotel_ids = {
        room["room_id"]: room["hotel_id"]
        for room in rooms
    }

    guest_ids = [g["guest_id"] for g in guests]

    for room in rooms:
        schedule = []
        cursor = ROOM_START

        while cursor < ROOM_END:
            gap = random.randint(1, 4)
            check_in = cursor + timedelta(days=gap)

            if check_in >= ROOM_END:
                break

            stay_length = random.randint(1, 5)
            check_out = min(
                check_in + timedelta(days=stay_length),
                ROOM_END
            )

            lead_days = random.randint(0, 60)

            booking_date = max(
                START_DATE,
                check_in - timedelta(days=lead_days)
            )

            # A booking cannot be made after the generation date.
            booking_date = min(booking_date, RUN_DATE)

            if check_out <= RUN_DATE:
                status = random.choices(
                    ["Completed", "Cancelled", "No-show"],
                    weights=[88, 8, 4]
                )[0]
            else:
                status = "Confirmed"

            booking_id = new_id()

            bookings.append({
                "booking_id": booking_id,
                "guest_id": random.choice(guest_ids),
                "hotel_id": hotel_ids[room["room_id"]],
                "room_id": room["room_id"],
                "booking_date": booking_date,
                "check_in_date": check_in,
                "check_out_date": check_out,
                "booking_status": status
            })

            schedule.append({
                "check_in": check_in,
                "check_out": check_out,
                "booking_id": booking_id,
                "status": status
            })

            cursor = check_out

        room_schedules[room["room_id"]] = schedule

    return bookings, room_schedules


# ============================================================
# 7. ROOM DAILY
# ============================================================

def generate_room_daily(rooms, room_schedules):
    path = OUTPUT_DIR / "fact_room_daily.csv"

    total_rows = 0

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "room_daily_id",
            "room_id",
            "hotel_id",
            "date_id",
            "booking_id",
            "is_sellable",
            "is_occupied",
            "room_revenue"
        ])

        for room_number, room in enumerate(rooms, start=1):
            schedule = room_schedules[room["room_id"]]
            schedule_index = 0

            current = ROOM_START

            while current < ROOM_END:

                # Move past completed booking intervals.
                while (
                    schedule_index < len(schedule)
                    and current >= schedule[schedule_index]["check_out"]
                ):
                    schedule_index += 1

                active_booking = None

                if schedule_index < len(schedule):
                    candidate = schedule[schedule_index]

                    if (
                        candidate["check_in"] <= current
                        < candidate["check_out"]
                    ):
                        active_booking = candidate

                occupied = (
                    active_booking is not None
                    and active_booking["status"]
                    in ["Completed", "Confirmed"]
                )

                # Maintenance rooms cannot be occupied.
                maintenance = (
                    not occupied and random.random() < 0.025
                )

                sellable = not maintenance

                booking_id = (
                    active_booking["booking_id"]
                    if occupied else None
                )

                revenue = 0.0

                if occupied:
                    # A small number of complimentary nights.
                    if random.random() >= 0.01:
                        season_multiplier = {
                            "Winter": 1.10,
                            "Summer": 1.05,
                            "Monsoon": 0.90,
                            "Post-Monsoon": 1.00
                        }[get_season(current.month)]

                        weekend_multiplier = (
                            1.12 if current.weekday() >= 5 else 1.0
                        )

                        revenue = (
                            room["base_rate"]
                            * season_multiplier
                            * weekend_multiplier
                            * random.uniform(0.90, 1.15)
                        )

                writer.writerow([
                    new_id(),
                    room["room_id"],
                    room["hotel_id"],
                    current.isoformat(),
                    booking_id or "",
                    int(sellable),
                    int(occupied),
                    f"{revenue:.2f}"
                ])

                total_rows += 1
                current += timedelta(days=1)

            if room_number % 100 == 0:
                print(
                    f"Room-night progress: {room_number:,}/{len(rooms):,} rooms "
                    f"({total_rows:,} rows)",
                    flush=True
                )

    print(f"Exported fact_room_daily: {total_rows:,} rows")


# ============================================================
# 8. GUEST FEEDBACK
# ============================================================

def generate_feedback(bookings):
    feedback = []

    comments = [
        "Excellent hospitality and friendly staff.",
        "Comfortable stay and clean rooms.",
        "Great location and good service.",
        "Food and room service could improve.",
        "The check-in experience was smooth.",
        "Beautiful property and pleasant atmosphere.",
        "Room maintenance needs improvement.",
        "Good value for money.",
        "Very satisfied with the overall experience."
    ]

    for booking in bookings:
        if booking["booking_status"] != "Completed":
            continue

        if random.random() > 0.65:
            continue

        earliest = booking["check_out_date"]

        latest = min(
            earliest + timedelta(days=30),
            RUN_DATE,
            ANALYSIS_END
        )

        if earliest > latest:
            continue

        feedback.append({
            "feedback_id": new_id(),
            "booking_id": booking["booking_id"],
            "guest_id": booking["guest_id"],
            "hotel_id": booking["hotel_id"],
            "feedback_date": random_date(earliest, latest),
            "rating": random.choices(
                [1, 2, 3, 4, 5],
                weights=[3, 5, 12, 35, 45]
            )[0],
            "comments": random.choice(comments)
        })

    return feedback


# ============================================================
# 9. VALIDATION BEFORE EXPORT
# ============================================================

def validate_data(
    hotels,
    rooms,
    guests,
    employees,
    dates,
    bookings,
    employment,
    feedback
):
    print("\nRunning pre-export validation...", flush=True)

    assert len(hotels) == 15
    assert len({h["hotel_id"] for h in hotels}) == 15

    city_counts = {}

    for hotel in hotels:
        city_counts[hotel["city"]] = (
            city_counts.get(hotel["city"], 0) + 1
        )

    assert all(count == 3 for count in city_counts.values())

    assert len({r["room_id"] for r in rooms}) == len(rooms)
    if MODE == "full":
        assert len(rooms) == 1500, f"Expected 1,500 rooms, found {len(rooms):,}"
        assert len(guests) == 15000, f"Expected 15,000 guests, found {len(guests):,}"
        assert len(employees) == 450, f"Expected 450 employees, found {len(employees):,}"
        assert len(dates) == 1827, f"Expected 1,827 dates, found {len(dates):,}"

    hotel_ids = {h["hotel_id"] for h in hotels}
    room_ids = {r["room_id"] for r in rooms}
    guest_ids = {g["guest_id"] for g in guests}
    employee_ids = {e["employee_id"] for e in employees}
    date_ids = {d["date_id"] for d in dates}
    booking_by_id = {b["booking_id"]: b for b in bookings}
    booking_ids = set(booking_by_id)
    assert len(booking_by_id) == len(bookings), "Duplicate booking_id found"

    assert all(r["hotel_id"] in hotel_ids for r in rooms)

    print(f"Validating {len(bookings):,} bookings...", flush=True)
    for booking in bookings:
        assert booking["room_id"] in room_ids
        assert booking["hotel_id"] in hotel_ids
        assert booking["guest_id"] in guest_ids
        assert booking["booking_date"] in date_ids
        assert booking["check_in_date"] in date_ids
        assert booking["check_out_date"] in date_ids
        assert booking["booking_date"] <= booking["check_in_date"]
        assert booking["check_out_date"] > booking["check_in_date"]

    feedback_booking_ids = set()

    print(f"Validating {len(feedback):,} feedback records...", flush=True)
    for item in feedback:
        assert item["booking_id"] in booking_ids
        assert item["guest_id"] in guest_ids
        assert item["feedback_date"] in date_ids
        assert 1 <= item["rating"] <= 5
        assert item["booking_id"] not in feedback_booking_ids
        feedback_booking_ids.add(item["booking_id"])

        # O(1) dictionary lookup instead of scanning all bookings for
        # every feedback row (which made full-mode validation extremely slow).
        booking = booking_by_id[item["booking_id"]]

        assert booking["booking_status"] == "Completed"
        assert item["guest_id"] == booking["guest_id"]
        assert item["hotel_id"] == booking["hotel_id"]
        assert item["feedback_date"] >= booking["check_out_date"]

    for item in employment:
        assert item["employee_id"] in employee_ids
        assert item["hotel_id"] in hotel_ids
        assert item["hire_date"] in date_ids

        if item["exit_date"] is not None:
            assert item["exit_date"] in date_ids
            assert item["exit_date"] > item["hire_date"]

    assert dates[0]["date_id"] == START_DATE
    assert dates[-1]["date_id"] == BOUNDARY_DATE

    print("Pre-export validation passed!")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 55)
    print("HORIZON HOSPITALITY DATA GENERATION")
    print("=" * 55)

    print(f"Mode: {MODE.upper()}")
    print(f"Generation date: {RUN_DATE}")
    print(f"Output directory: {OUTPUT_DIR}")

    print("\nGenerating dimensions...")

    hotels = generate_hotels()
    rooms = generate_rooms(hotels)
    guests = generate_guests()
    employees, employment = generate_employees(hotels)
    dates = generate_dates()

    print("\nGenerating bookings...", flush=True)
    bookings, room_schedules = generate_bookings(
        rooms, hotels, guests
    )

    print("\nGenerating guest feedback...", flush=True)
    feedback = generate_feedback(bookings)

    validate_data(
        hotels,
        rooms,
        guests,
        employees,
        dates,
        bookings,
        employment,
        feedback
    )

    print("\nExporting dimension and fact tables...")

    save_dataframe("dim_hotels", hotels)
    save_dataframe("dim_rooms", rooms)
    save_dataframe("dim_guests", guests)
    save_dataframe("dim_employees", employees)
    save_dataframe("dim_date", dates)

    save_dataframe("fact_bookings", bookings)
    save_dataframe("fact_guest_feedback", feedback)
    save_dataframe("fact_employee_employment", employment)

    print("\nGenerating room-night records...")
    generate_room_daily(rooms, room_schedules)

    # Save generation metadata.
    metadata = {
        "project": "Horizon Hospitality Group",
        "generation_date": str(RUN_DATE),
        "mode": MODE,
        "analysis_start": str(START_DATE),
        "analysis_end": str(ANALYSIS_END),
        "date_dimension_end": str(BOUNDARY_DATE),
        "synthetic_data": True,
        "future_records_are_simulated": True
    }

    pd.DataFrame([metadata]).to_csv(
        OUTPUT_DIR / "generation_metadata.csv",
        index=False
    )

    print("\n" + "=" * 55)
    print("DATA GENERATION COMPLETED")
    print("=" * 55)
    print(f"Hotels: {len(hotels):,}")
    print(f"Rooms: {len(rooms):,}")
    print(f"Guests: {len(guests):,}")
    print(f"Employees: {len(employees):,}")
    print(f"Dates: {len(dates):,}")
    print(f"Bookings: {len(bookings):,}")
    print(f"Feedback: {len(feedback):,}")
    print(f"Employment periods: {len(employment):,}")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
