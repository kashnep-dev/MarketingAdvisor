import os

import streamlit as st

work_dir = os.path.dirname(os.path.abspath((__file__)))
os.environ["WORK_DIR"] = work_dir


def _set_pages():
    dashboard = st.Page(
        "app_pages/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True
    )
    page_1 = st.Page("app_pages/generate_stream.py", title="광고 생성 봇", icon=":material/search:")
    page_2 = st.Page("app_pages/review_stream.py", title="광고 심의 봇", icon=":material/history:")

    pg = st.navigation(
        {
            "Reports": [dashboard],
            "Advisor": [page_1, page_2],
        }
    )
    pg.run()


if __name__ == "__main__":
    # subprocess.run(["redis-server"])
    _set_pages()
    # redis.startup()
