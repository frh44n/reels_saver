import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

def get_db_connection():
    conn = psycopg2.connect(Config.DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        chat_id BIGINT PRIMARY KEY,
        video_count INTEGER DEFAULT 0
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_or_create_user(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE chat_id = %s;", (chat_id,))
    user = cur.fetchone()
    if not user:
        cur.execute("INSERT INTO users (chat_id, video_count) VALUES (%s, 0) RETURNING *;", (chat_id,))
        user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return user

def increment_video_count(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET video_count = video_count + 1 WHERE chat_id = %s;", (chat_id,))
    conn.commit()
    cur.close()
    conn.close()
