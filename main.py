import os
import psutil
import subprocess
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


if __name__ == "__main__":
    start_redis()
    _set_pages()
    # redis.startup()
