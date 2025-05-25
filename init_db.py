import sqlite3
import os

def init_db():
    db_path = os.path.abspath("rcmis.db")
    print(f"[INFO] Creating database at: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                dob TEXT NOT NULL,
                age INTEGER NOT NULL,
                position TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS injuries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                injury_type TEXT NOT NULL,
                body_part TEXT NOT NULL,
                severity TEXT NOT NULL,
                date_logged TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rehab (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                injury_id INTEGER NOT NULL,
                notes TEXT,
                status TEXT,
                date_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (injury_id) REFERENCES injuries(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS availability (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                day TEXT NOT NULL,
                available INTEGER NOT NULL,
                reason TEXT,
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
        ''')
        cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_selection (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id TEXT NOT NULL,
        team TEXT NOT NULL,
        FOREIGN KEY (player_id) REFERENCES players(player_id)
    )
''')
        cursor.execute('''
    CREATE TABLE IF NOT EXISTS strapping (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id TEXT NOT NULL,
        needs_strapping INTEGER NOT NULL,
        FOREIGN KEY (player_id) REFERENCES players(player_id)
    )
''')

        conn.commit()
        print("[SUCCESS] Tables created successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("[RUNNING] init_db.py is being executed")
    init_db()