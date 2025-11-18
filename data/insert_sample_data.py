import sqlite3
import os

DB_PATH = os.path.join("data", "haken_connect.db")

def insert_sample_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    companies = [
        ("C001", "株式会社テック"),
        ("C002", "大阪製造株式会社"),
    ]
    c.executemany("INSERT OR IGNORE INTO companies (company_id, company_name) VALUES (?, ?)", companies)
    agencies = [
        ("A001", "東京派遣サービス"),
        ("A002", "大阪人材社"),
    ]
    c.executemany("INSERT OR IGNORE INTO agencies (agency_id, agency_name) VALUES (?, ?)", agencies)
    opportunities = [
        ("OP001", "C001", "東京", "IT", "A", "エンジニア", 3, "Python経験必須"),
        ("OP002", "C002", "大阪", "製造", "B", "検査員", 5, "未経験OK"),
    ]
    c.executemany(
        "INSERT OR IGNORE INTO opportunities (opportunity_id, company_id, region, industry, need_level, role, headcount_needed, requirements) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        opportunities
    )
    conn.commit()
    conn.close()
