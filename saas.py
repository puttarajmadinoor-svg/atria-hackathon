from fastapi import FastAPI, Header
from typing import Optional
import uvicorn
import sqlite3
import json

app = FastAPI(title="SENTINEL SaaS")

# --- Database Helper ---
def get_db():
    conn = sqlite3.connect("sentinel.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS tenants (id INTEGER PRIMARY KEY, name TEXT UNIQUE, region TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, tenant TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS incidents (id INTEGER PRIMARY KEY, tenant TEXT, reason TEXT, confidence INTEGER, status TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, tenant TEXT, server TEXT, cpu INTEGER, memory INTEGER, latency INTEGER)")
    conn.execute("INSERT OR IGNORE INTO tenants VALUES (1, 'TechCorp_Bangalore', 'India')")
    conn.execute("INSERT OR IGNORE INTO tenants VALUES (2, 'TechCorp_Singapore', 'Singapore')")
    conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'TechCorp_Bangalore')")
    conn.commit()
    conn.close()

init_db()

# --- 1. INGEST API - Collector sends data here ---
@app.post("/ingest")
def ingest(data: dict, x_tenant_id: Optional[str] = Header(None)):
    tenant = x_tenant_id or data.get("tenant", "TechCorp_Bangalore")

    # SECURITY: Block if secret/password found - Your Viva Feature
    if "password" in str(data).lower():
        return {"status": "BLOCKED", "reason": "Secret detected in payload"}

    # Save to Database
    conn = get_db()
    conn.execute("INSERT INTO logs (tenant, server, cpu, memory, latency) VALUES (?, ?, ?, ?, ?)",
                 (tenant, data.get("server", "Server 1"), data.get("cpu", 0), data.get("memory", 0), data.get("latency", 0)))
    conn.commit()
    conn.close()
    return {"status": "OK", "tenant": tenant, "stored_id": "saved_to_db"}

# --- 2. DASHBOARD API - Frontend reads from here ---
@app.get("/dashboard/{tenant}")
def get_dashboard(tenant: str):
    conn = get_db()
    logs = conn.execute("SELECT * FROM logs WHERE tenant=? ORDER BY id DESC LIMIT 10", (tenant,)).fetchall()
    conn.close()
    # Multi-Org Isolation: Only this tenant's data returned
    return {"tenant": tenant, "records": [dict(r) for r in logs]}

# --- 3. LOGIN API ---
@app.post("/login")
def login(username: str, password: str):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    conn.close()
    if user:
        return {"success": True, "tenant": user["tenant"], "user": user["username"]}
    return {"success": False, "message": "Wrong login"}

# --- 4. BLOCK IP API - AIOps Action ---
@app.post("/block-ip")
def block_ip(tenant: str, ip: str):
    conn = get_db()
    conn.execute("INSERT INTO incidents (tenant, reason, confidence, status) VALUES (?, ?, ?, ?)",
                 (tenant, f"Blocked IP {ip}", 92, "Resolved"))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"IP {ip} blocked for {tenant}"}

@app.get("/")
def home():
    return {"service": "SENTINEL SaaS is Running", "tenants": ["TechCorp_Bangalore", "TechCorp_Singapore"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)