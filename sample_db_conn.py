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
    # The connection context manager will automatically COMMIT changes if successful,
    # or ROLLBACK if an error occurs.
    with psycopg.connect(**conn_params) as conn:
        
        # The cursor context manager automatically CLOSES the cursor when done
        with conn.cursor() as cur:
            
            # --- Example 1: Creating a table --- ONLY if the table is not in the database already
            cur.execute("""
                CREATE TABLE IF NOT EXISTS animals (
                    animalid SERIAL PRIMARY KEY,
                    animalname VARCHAR(100) UNIQUE,
                    speciestype VARCHAR(100),
                    age INTEGER  
                );
            """)

except Exception as error:
    print(f"Error connecting to database: {error}")
