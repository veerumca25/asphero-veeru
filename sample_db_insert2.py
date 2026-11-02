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
            # --- Example 3: Inserting multiple records into the table ---
            animals_to_insert = [
                ("Max", "Dog", 3),
                ("Whiskers", "Cat", 2),
                ("Buddy", "Dog", 4),
                ("Mittens", "Cat", 1)
            ]

            cur.executemany("""
                INSERT INTO animals (animalname, speciestype, age)
                VALUES (%s, %s, %s)
                ON CONFLICT (animalname) DO NOTHING;  -- Avoid inserting duplicates
            """, animals_to_insert)
        conn.commit()  # Commit the transaction to save changes
except Exception as error:
    print(f"Error connecting to database: {error}")    