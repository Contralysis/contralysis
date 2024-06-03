import sqlite3

def init_db():
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results
                 (id INTEGER PRIMARY KEY, address TEXT, report TEXT)''')
    conn.commit()
    conn.close()

def save_report(address, report):
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute("INSERT INTO results (address, report) VALUES (?, ?)", (address, report))
    conn.commit()
    conn.close()

def get_report(address):
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute("SELECT report FROM results WHERE address=?", (address,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None
