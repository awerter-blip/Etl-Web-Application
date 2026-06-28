import sqlite3
import psycopg2

#DB_NAME = "chat.db"

#def get_connection():
#    return sqlite3.connect(DB_NAME)

def get_connection():
    conn = psycopg2.connect(
    host="aws-0-eu-west-1.pooler.supabase.com",
    database="postgres",
    user="postgres.zzlzecfpkbyerfpoqjwj",
    password="Etlmusic19871206?",
    port=5432)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        name TEXT,
        password TEXT
        
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        chat_type INTEGER,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS logins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS tokens (
        token TEXT PRIMARY KEY,
        user_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")

    conn.commit()
    conn.close()