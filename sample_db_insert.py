import os

import psycopg


conn_params = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "Adgj@135712",
    "host": "localhost",
    "port": "5432",
    "options": "-c search_path=animal_mgmt,public"  # changing the default schema 
}

try:

 with psycopg.connect(**conn_params) as conn:

    with conn.cursor() as cur:
        # --- Example 2: Inserting a record into the table ---
        cur.execute("""
            INSERT INTO animals (animalname, speciestype, age)
            VALUES (%s, %s, %s)
            ON CONFLICT (animalname) DO NOTHING;  -- Avoid inserting duplicates
        """, ("Leo", "Lion", 5))

except Exception as error:
    print(f"Error connecting to database: {error}")