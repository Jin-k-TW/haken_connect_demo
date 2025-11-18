import sqlite3
import os

DB_PATH = os.path.join("data", "haken_connect.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS opportunities (
        opportunity_id TEXT PRIMARY KEY,
        company_id TEXT,
        region TEXT,
        industry TEXT,
        need_level TEXT,
        role TEXT,
        headcount_needed INTEGER,
        requirements TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS companies (
        company_id TEXT PRIMARY KEY,
        company_name TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS agencies (
        agency_id TEXT PRIMARY KEY,
        agency_name TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS connections (
        connection_id TEXT PRIMARY KEY,
        timestamp TEXT,
        agency_id TEXT,
        opportunity_id TEXT,
        status TEXT,
        fee_amount INTEGER,
        incentive_amount INTEGER,
        notes TEXT
    )''')
    conn.commit()
    conn.close()
