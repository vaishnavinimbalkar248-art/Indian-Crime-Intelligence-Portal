import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'indian_crime_data_2021_2026_with_names.csv')
DB_PATH = os.path.join(BASE_DIR, 'database', 'crime_portal.db')

def init_db():
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return

    print("Loading CSV data into SQLite database...")
    df = pd.read_csv(CSV_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Crimes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crimes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Age INTEGER,
            Gender TEXT,
            State TEXT,
            City TEXT,
            Crime_Type TEXT,
            Location TEXT,
            Arrest TEXT,
            Date TEXT
        )
    ''')

    # Create Officers Table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS officers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            badge_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            designation TEXT NOT NULL
        )
    ''')

    # Seed default prototype officer
    cursor.execute('''
        INSERT OR IGNORE INTO officers (badge_id, password, name, designation)
        VALUES ('OFFICER123', 'admin123', 'Inspector Sharma', 'Senior Crime Analyst')
    ''')

    # Load records from DataFrame into SQLite table
    df.to_sql('crimes', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()
    print(f"SUCCESS: Database created at {DB_PATH} with {len(df)} records!")

if __name__ == '__main__':
    init_db()