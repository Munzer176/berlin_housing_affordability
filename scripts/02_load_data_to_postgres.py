"""
Berlin Housing Affordability Project
Step 2: Load CSV data into PostgreSQL

HOW TO RUN:
    1. Make sure PostgreSQL is running and database 'berlin_housing' exists
       (run 01_setup_postgres.sql first)
    2. Update DB_CONFIG below with your PostgreSQL credentials
    3. Run:
       python3 scripts/02_load_data_to_postgres.py

REQUIREMENTS:
    pip install pandas psycopg2-binary sqlalchemy
"""

import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
import sys

# ============================================================
# DATABASE CONFIG - UPDATE THESE WITH YOUR SETTINGS
# ============================================================
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "berlin_housing",
    "user": "postgres",      # <-- Change if needed
    "password": "postgres",  # <-- Change if needed
}

# Build connection string
conn_string = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# ============================================================
# PROJECT PATHS
# ============================================================
project_root = Path(__file__).resolve().parent.parent
raw_path = project_root / "data" / "raw"
processed_path = project_root / "data" / "processed"

# ============================================================
# CSV FILES TO LOAD
# ============================================================
CSV_TO_TABLE = {
    processed_path / "berlin_core_clean.csv": "raw_housing_listings",
    raw_path / "berlin_income_by_district.csv": "raw_income_by_district",
    processed_path / "social_atlas_clean.csv": "raw_social_atlas",
    processed_path / "rent_clean.csv": "raw_rent_prices",
}

# ============================================================
# COLUMN NAME MAPPINGS
# ============================================================
COLUMN_MAPS = {
    "berlin_core_clean.csv": {
        "baseRent": "base_rent",
        "totalRent": "total_rent",
        "livingSpace": "living_space",
        "noRooms": "no_rooms",
        "numberOfFloors": "number_of_floors",
        "yearConstructed": "year_constructed",
        "interiorQual": "interior_qual",
        "hasKitchen": "has_kitchen",
        "typeOfFlat": "type_of_flat",
        "serviceCharge": "service_charge",
        "heatingType": "heating_type",
        "newlyConst": "newly_const",
        "picturecount": "picture_count",
        "pricetrend": "price_trend",
        "date": "date_period",
    },
    "social_atlas_clean.csv": {
        "GESIx_2013": "gesix_2013",
        "GESIx_2022": "gesix_2022",
        "ESIx_2013": "esix_2013",
        "ESIx_2022": "esix_2022",
        "DI_2013": "di_2013",
        "DI_2022": "di_2022",
        "DII_2013": "dii_2013",
        "DII_2022": "dii_2022",
        "DIII_2013": "diii_2013",
        "DIII_2022": "diii_2022",
    },
    "rent_clean.csv": {},
    "berlin_income_by_district.csv": {},
}

def main():
    print("=" * 60)
    print("  LOADING CSV DATA INTO POSTGRESQL")
    print("=" * 60)

    # Connect to database
    try:
        engine = create_engine(conn_string)
        with engine.connect() as conn:
            print(f"Connected to PostgreSQL: {DB_CONFIG['database']}")
    except Exception as e:
        print("ERROR: Could not connect to PostgreSQL!")
        print(f"  {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print(f"  2. Database '{DB_CONFIG['database']}' exists")
        print("  3. Credentials in DB_CONFIG are correct")
        sys.exit(1)

    # Load each CSV
    for filepath, table_name in CSV_TO_TABLE.items():
        if not filepath.exists():
            print(f"\n  SKIP: {filepath.name} not found at {filepath}")
            continue

        print(f"\n  Loading {filepath.name} -> {table_name}...")

        # Read CSV
        df = pd.read_csv(filepath)
        original_rows = len(df)

        # Rename columns if mapping exists
        col_map = COLUMN_MAPS.get(filepath.name, {})
        if col_map:
            df = df.rename(columns=col_map)

        # Convert column names to snake_case
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]

        # Remove 'id' column if it exists (let PostgreSQL auto-generate)
        if "id" in df.columns:
            df = df.drop(columns=["id"])

        try:
            # Clear table first, then append
            with engine.begin() as conn:
                conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY"))

            df.to_sql(table_name, engine, if_exists="append", index=False, method="multi")
            print(f"    Loaded {original_rows:,} rows into {table_name}")

        except Exception as e:
            print(f"    ERROR loading {filepath.name}: {e}")

    # Verify
    print("\n" + "=" * 60)
    print("  VERIFICATION")
    print("=" * 60)

    with engine.connect() as conn:
        for table_name in CSV_TO_TABLE.values():
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                print(f"  {table_name}: {count:,} rows")
            except Exception as e:
                print(f"  {table_name}: ERROR - {e}")

    print("\nAll data loaded successfully!")
    print("Next step: continue SQL analysis queries.")

if __name__ == "__main__":
    main()