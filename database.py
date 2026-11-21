import sqlite3

def init_db():
    conn = sqlite3.connect("sentinel.db")
    c = conn.cursor()

    # 1. Tenants Table - For Multi-Org
    c.execute("CREATE TABLE IF NOT EXISTS tenants (id INTEGER PRIMARY KEY, name TEXT UNIQUE, region TEXT)")

    # 2. Users Table - For Login
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, tenant TEXT)")

    # 3. Incidents Table - For AIOps
    c.execute("CREATE TABLE IF NOT EXISTS incidents (id INTEGER PRIMARY KEY, tenant TEXT, reason TEXT, confidence INTEGER, status TEXT)")

    # Demo Data
    c.execute("INSERT OR IGNORE INTO tenants VALUES (1, 'TechCorp_Bangalore', 'India')")
    c.execute("INSERT OR IGNORE INTO tenants VALUES (2, 'TechCorp_Singapore', 'Singapore')")
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'TechCorp_Bangalore')")
    c.execute("INSERT OR IGNORE INTO users VALUES (2, 'student1', 'pass123', 'TechCorp_Singapore')")

    conn.commit()
    conn.close()
    print("Database Ready: sentinel.db created")

if __name__ == "__main__":
    init_db()