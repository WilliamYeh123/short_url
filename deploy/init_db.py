import sqlite3

# database initialization
def init_db():
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            short TEXT UNIQUE NOT NULL,
            create_at REAL DEFAULT CURRENT_TIMESTAMP,
            expire REAL
        )
    ''')
    conn.commit()
    conn.close()