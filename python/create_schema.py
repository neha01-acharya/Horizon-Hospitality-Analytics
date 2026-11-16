
from config import get_connection
import mysql.connector

DATABASE = "horizon_hospitality"

TABLES = [

    # 1. HOTELS
    """
    CREATE TABLE IF NOT EXISTS dim_hotels (
        hotel_id CHAR(36) PRIMARY KEY,
        hotel_name VARCHAR(150) NOT NULL UNIQUE,
        city VARCHAR(50) NOT NULL,
        state VARCHAR(50) NOT NULL,
        hotel_type VARCHAR(50) NOT NULL,
        star_rating DECIMAL(2,1) NOT NULL,
        CHECK (star_rating BETWEEN 1 AND 5)
    ) ENGINE=InnoDB
    """,

    # 2. ROOMS
    """
    CREATE TABLE IF NOT EXISTS dim_rooms (
        room_id CHAR(36) PRIMARY KEY,
        hotel_id CHAR(36) NOT NULL,
        room_number VARCHAR(20) NOT NULL,
        room_type VARCHAR(50) NOT NULL,
        base_rate DECIMAL(10,2) NOT NULL,

        UNIQUE (hotel_id, room_number),

        CONSTRAINT fk_rooms_hotel
            FOREIGN KEY (hotel_id)
            REFERENCES dim_hotels(hotel_id),

        CHECK (base_rate >= 0)
    ) ENGINE=InnoDB
    """,

    # 3. GUESTS
    """
    CREATE TABLE IF NOT EXISTS dim_guests (
        guest_id CHAR(36) PRIMARY KEY,
        guest_name VARCHAR(150) NOT NULL,
        age_group VARCHAR(30),
        guest_segment VARCHAR(50)
    ) ENGINE=InnoDB
    """,

    # 4. EMPLOYEES
    """
    CREATE TABLE IF NOT EXISTS dim_employees (
        employee_id CHAR(36) PRIMARY KEY,
        employee_name VARCHAR(150) NOT NULL
    ) ENGINE=InnoDB
    """,

    # 5. DATE DIMENSION
    """
    CREATE TABLE IF NOT EXISTS dim_date (
        date_id DATE PRIMARY KEY,
        `year` SMALLINT NOT NULL,
        month TINYINT NOT NULL,
        month_name VARCHAR(15) NOT NULL,
        quarter TINYINT NOT NULL,
        day_of_month TINYINT NOT NULL,
        day_of_week VARCHAR(15) NOT NULL,
        season VARCHAR(30) NOT NULL,
        is_weekend BOOLEAN NOT NULL,

        CHECK (month BETWEEN 1 AND 12),
        CHECK (quarter BETWEEN 1 AND 4),
        CHECK (day_of_month BETWEEN 1 AND 31)
    ) ENGINE=InnoDB
    """,

    # 6. BOOKINGS
    """
    CREATE TABLE IF NOT EXISTS fact_bookings (
        booking_id CHAR(36) PRIMARY KEY,
        guest_id CHAR(36) NOT NULL,
        hotel_id CHAR(36) NOT NULL,
        room_id CHAR(36) NOT NULL,
        booking_date DATE NOT NULL,
        check_in_date DATE NOT NULL,
        check_out_date DATE NOT NULL,
        booking_status VARCHAR(20) NOT NULL,

        CONSTRAINT fk_booking_guest
            FOREIGN KEY (guest_id)
            REFERENCES dim_guests(guest_id),

        CONSTRAINT fk_booking_hotel
            FOREIGN KEY (hotel_id)
            REFERENCES dim_hotels(hotel_id),

        CONSTRAINT fk_booking_room
            FOREIGN KEY (room_id)
            REFERENCES dim_rooms(room_id),

        CONSTRAINT fk_booking_date
            FOREIGN KEY (booking_date)
            REFERENCES dim_date(date_id),

        CONSTRAINT fk_booking_checkin
            FOREIGN KEY (check_in_date)
            REFERENCES dim_date(date_id),

        CONSTRAINT fk_booking_checkout
            FOREIGN KEY (check_out_date)
            REFERENCES dim_date(date_id),

        CHECK (booking_status IN
            ('Confirmed', 'Completed', 'Cancelled', 'No-show')),

        CHECK (booking_date <= check_in_date),
        CHECK (check_out_date > check_in_date),

        INDEX idx_booking_hotel (hotel_id),
        INDEX idx_booking_guest (guest_id),
        INDEX idx_booking_room_dates (room_id, check_in_date, check_out_date)
    ) ENGINE=InnoDB
    """,

    # 7. DAILY ROOM PERFORMANCE
    """
    CREATE TABLE IF NOT EXISTS fact_room_daily (
        room_daily_id CHAR(36) PRIMARY KEY,
        room_id CHAR(36) NOT NULL,
        hotel_id CHAR(36) NOT NULL,
        date_id DATE NOT NULL,
        booking_id CHAR(36),
        is_sellable BOOLEAN NOT NULL,
        is_occupied BOOLEAN NOT NULL,
        room_revenue DECIMAL(10,2) NOT NULL,

        UNIQUE (room_id, date_id),

        CONSTRAINT fk_daily_room
            FOREIGN KEY (room_id)
            REFERENCES dim_rooms(room_id),

        CONSTRAINT fk_daily_hotel
            FOREIGN KEY (hotel_id)
            REFERENCES dim_hotels(hotel_id),

        CONSTRAINT fk_daily_date
            FOREIGN KEY (date_id)
            REFERENCES dim_date(date_id),

        CONSTRAINT fk_daily_booking
            FOREIGN KEY (booking_id)
            REFERENCES fact_bookings(booking_id),

        CHECK (room_revenue >= 0),
        CHECK (is_occupied = 0 OR is_sellable = 1),

        CHECK (
            (is_occupied = 1 AND booking_id IS NOT NULL)
            OR
            (is_occupied = 0 AND booking_id IS NULL
             AND room_revenue = 0)
        ),

        INDEX idx_daily_hotel_date (hotel_id, date_id),
        INDEX idx_daily_date (date_id)
    ) ENGINE=InnoDB
    """,

    # 8. GUEST FEEDBACK
    """
    CREATE TABLE IF NOT EXISTS fact_guest_feedback (
        feedback_id CHAR(36) PRIMARY KEY,
        booking_id CHAR(36) NOT NULL UNIQUE,
        guest_id CHAR(36) NOT NULL,
        hotel_id CHAR(36) NOT NULL,
        feedback_date DATE NOT NULL,
        rating TINYINT NOT NULL,
        comments TEXT,

        CONSTRAINT fk_feedback_booking
            FOREIGN KEY (booking_id)
            REFERENCES fact_bookings(booking_id),

        CONSTRAINT fk_feedback_guest
            FOREIGN KEY (guest_id)
            REFERENCES dim_guests(guest_id),

        CONSTRAINT fk_feedback_hotel
            FOREIGN KEY (hotel_id)
            REFERENCES dim_hotels(hotel_id),

        CONSTRAINT fk_feedback_date
            FOREIGN KEY (feedback_date)
            REFERENCES dim_date(date_id),

        CHECK (rating BETWEEN 1 AND 5),

        INDEX idx_feedback_hotel (hotel_id),
        INDEX idx_feedback_date (feedback_date)
    ) ENGINE=InnoDB
    """,

    # 9. EMPLOYMENT HISTORY
    """
    CREATE TABLE IF NOT EXISTS fact_employee_employment (
        employment_id CHAR(36) PRIMARY KEY,
        employee_id CHAR(36) NOT NULL,
        hotel_id CHAR(36) NOT NULL,
        department VARCHAR(80) NOT NULL,
        position VARCHAR(100) NOT NULL,
        hire_date DATE NOT NULL,
        exit_date DATE,
        separation_type VARCHAR(30),
        exit_reason VARCHAR(100),

        CONSTRAINT fk_employment_employee
            FOREIGN KEY (employee_id)
            REFERENCES dim_employees(employee_id),

        CONSTRAINT fk_employment_hotel
            FOREIGN KEY (hotel_id)
            REFERENCES dim_hotels(hotel_id),

        CONSTRAINT fk_employment_hire
            FOREIGN KEY (hire_date)
            REFERENCES dim_date(date_id),

        CONSTRAINT fk_employment_exit
            FOREIGN KEY (exit_date)
            REFERENCES dim_date(date_id),

        CHECK (exit_date IS NULL OR exit_date > hire_date),

        CHECK (
            separation_type IS NULL
            OR separation_type IN ('company_exit', 'internal_transfer')
        ),

        CHECK (
            (exit_date IS NULL AND separation_type IS NULL)
            OR
            (exit_date IS NOT NULL AND separation_type IS NOT NULL)
        ),

        INDEX idx_employment_employee (employee_id),
        INDEX idx_employment_hotel (hotel_id),
        INDEX idx_employment_dates (hire_date, exit_date)
    ) ENGINE=InnoDB
    """
]


def create_database():
    connection = get_connection(include_database=False)
    cursor = connection.cursor()

    try:
        cursor.execute(
            f"""
            CREATE DATABASE IF NOT EXISTS `{DATABASE}`
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_0900_ai_ci
            """
        )
        print(f"Database '{DATABASE}' is ready.")

    finally:
        cursor.close()
        connection.close()


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        for index, statement in enumerate(TABLES, start=1):
            cursor.execute(statement)
            print(f"Table {index}/9 created successfully.")

        connection.commit()
        print("\nAll nine tables created successfully!")

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    create_database()
    create_tables()
