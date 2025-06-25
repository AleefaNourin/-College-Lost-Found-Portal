import sqlite3

conn = sqlite3.connect('database.db')
conn.execute('''
    CREATE TABLE items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        type TEXT NOT NULL,
        image TEXT NOT NULL,
        contact_info TEXT NOT NULL,
        approved INTEGER DEFAULT 0
    )
''')
conn.close()

print("Database created and table initialized.")
