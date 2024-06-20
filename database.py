# database.py

import psycopg2
from config import Config

def init_db():
    with psycopg2.connect(Config.DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id BIGINT PRIMARY KEY,
                video_count INT DEFAULT 0
            );
            """)
            conn.commit()

def create_custom_table():
    with psycopg2.connect(Config.DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS your_table_name (
                id SERIAL PRIMARY KEY,
                column1 TEXT,
                column2 TEXT
            );
            """)
            conn.commit()

def get_or_create_user(chat_id):
    with psycopg2.connect(Config.DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
            user = cursor.fetchone()
            if not user:
                cursor.execute("INSERT INTO users (chat_id, video_count) VALUES (%s, %s)", (chat_id, 0))
                conn.commit()

def increment_video_count(chat_id):
    with psycopg2.connect(Config.DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET video_count = video_count + 1 WHERE chat_id = %s", (chat_id,))
            conn.commit()
