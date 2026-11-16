
import csv
from pathlib import Path

from config import get_connection


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "generated_data"

BATCH_SIZE = 1000

# Parent tables before dependent fact tables
LOAD_ORDER = [
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

BOOLEAN_COLUMNS = {
    "is_weekend",
    "is_sellable",
    "is_occupied",
}


# --------------------------------------------------
# CSV ROW CONVERSION
# --------------------------------------------------

def clean_row(row):
    cleaned = {}

    for column, value in row.items():

        if value is None or value.strip() == "":
            cleaned[column] = None

        elif column in BOOLEAN_COLUMNS:
            cleaned[column] = (
                1 if value.strip().lower() in {"true", "1"} else 0
            )

        else:
            cleaned[column] = value

    return cleaned


# --------------------------------------------------
# LOAD ONE TABLE
# --------------------------------------------------

def load_table(cursor, table_name):

    file_path = DATA_DIR / f"{table_name}.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {file_path}"
        )

    with open(file_path, "r", newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)
        columns = reader.fieldnames

        if not columns:
            raise ValueError(f"No columns found in {file_path.name}")

        column_sql = ", ".join(
            f"`{column}`" for column in columns
        )

        placeholders = ", ".join(
            ["%s"] * len(columns)
        )

        insert_sql = (
            f"INSERT INTO `{table_name}` "
            f"({column_sql}) VALUES ({placeholders})"
        )

        batch = []
        total_inserted = 0

        for row in reader:

            cleaned = clean_row(row)

            batch.append(
                tuple(cleaned[column] for column in columns)
            )

            if len(batch) >= BATCH_SIZE:

                cursor.executemany(insert_sql, batch)
                total_inserted += len(batch)
                batch.clear()

        # Insert remaining rows
        if batch:
            cursor.executemany(insert_sql, batch)
            total_inserted += len(batch)

    print(f"Loaded {table_name}: {total_inserted:,} rows")

    return total_inserted


# --------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------

def main():

    print("\n" + "=" * 55)
    print("HORIZON HOSPITALITY - MYSQL DATA LOADING")
    print("=" * 55)

    connection = None
    cursor = None

    try:
        connection = get_connection(include_database=True)
        cursor = connection.cursor()

        # Safety check: do not accidentally duplicate existing data
        print("\nChecking existing table records...")

        existing_counts = {}

        for table in LOAD_ORDER:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            existing_counts[table] = cursor.fetchone()[0]

        non_empty = {
            table: count
            for table, count in existing_counts.items()
            if count > 0
        }

        if non_empty:
            raise RuntimeError(
                "Some tables already contain records. "
                f"Loading stopped to prevent duplicates: {non_empty}"
            )

        print("All nine tables are empty. Safe to load.")

        # Load all tables in one transaction
        loaded_counts = {}

        print("\nStarting batch inserts...\n")

        for table in LOAD_ORDER:
            loaded_counts[table] = load_table(cursor, table)

        connection.commit()

        print("\n" + "=" * 55)
        print("MYSQL LOADING COMPLETED")
        print("=" * 55)

        print("\nVerifying MySQL row counts...\n")

        all_match = True

        for table in LOAD_ORDER:

            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            actual_count = cursor.fetchone()[0]

            expected_count = loaded_counts[table]

            status = "PASS" if actual_count == expected_count else "FAIL"

            print(
                f"{table:<32} "
                f"CSV: {expected_count:>7,} | "
                f"MySQL: {actual_count:>7,} | "
                f"{status}"
            )

            if actual_count != expected_count:
                all_match = False

        if not all_match:
            raise RuntimeError("MySQL row-count reconciliation failed.")

        print("\nALL TABLES LOADED AND RECONCILED SUCCESSFULLY!")

    except Exception as exc:

        if connection and connection.is_connected():
            connection.rollback()

        print("\nDATA LOADING FAILED")
        print(f"Error: {exc}")

        raise

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

        print("\nMySQL connection closed.")


if __name__ == "__main__":
    main()
