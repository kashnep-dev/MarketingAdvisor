import os
import sqlite3
import subprocess

import psutil
import streamlit as st

work_dir = os.path.dirname(os.path.abspath((__file__)))
os.environ["WORK_DIR"] = work_dir


def _set_pages():
    dashboard = st.Page(
        "app_pages/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True
    )
    prompts = st.Page(
        "app_pages/prompts.py", title="Prompts", icon=":material/robot:"
    )
    page_1 = st.Page("app_pages/generate_stream.py", title="광고 생성 봇", icon=":material/search:")
    page_2 = st.Page("app_pages/review_stream.py", title="광고 심의 봇", icon=":material/history:")

    pg = st.navigation(
        {
            "Reports": [dashboard, prompts],
            "Advisor": [page_1, page_2],
        }
    )
    pg.run()


def is_redis_running():
    """Check if Redis server is running."""
    for process in psutil.process_iter(['name', 'cmdline']):
        if 'redis-server' in process.info['name'] or any('redis-server' in arg for arg in process.info['cmdline']):
            return True
    return False


def start_redis():
    """Start Redis server if not already running and if OS is not Windows."""
    if os.name == 'posix':  # UNIX 계열 운영 체제 확인
        if not is_redis_running():
            print("Starting Redis server...")
            subprocess.run(["redis-server"])
        else:
            print("Redis server is already running.")
    else:
        print("This code is only for UNIX-based systems.")


def create_tables():
    conn = sqlite3.connect("shcard.db")
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS tb_trace (
                trace_id TEXT NOT NULL,
                trace_content TEXT NOT NULL,
                trace_order INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                prompt_id TEXT,
                input_time TIMESTAMP NOT NULL,
                user_input_yn INTEGER NOT NULL,  -- SQLite는 BOOLEAN을 지원하지 않으므로 INTEGER로 사용 (0: False, 1: True)
                user_input_text TEXT,
                usage_cost REAL NOT NULL,
                usage_token_count INTEGER NOT NULL,
                PRIMARY KEY (trace_id)
            )
        """)
    conn.commit()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_generation (
            generation_id TEXT NOT NULL,
            generation_order INTEGER NOT NULL,
            generation_text TEXT NOT NULL,
            response_start_time_stream TIMESTAMP,
            response_end_time TIMESTAMP,
            response_duration_time INTEGER,
            response_start_time TIMESTAMP NOT NULL,
            user_expose_step INTEGER NOT NULL,  -- BOOLEAN 대신 INTEGER 사용 (0: False, 1: True)
            user_expose_text TEXT,
            usage_cost REAL NOT NULL,
            usage_token_count INTEGER NOT NULL,
            usage_model_name TEXT NOT NULL,
            PRIMARY KEY (generation_id)
        )
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    start_redis()
    _set_pages()
    create_tables()
    # redis.startup()
