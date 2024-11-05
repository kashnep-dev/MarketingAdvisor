import os
import subprocess

import streamlit as st
from langchain.callbacks.tracers import LangChainTracer
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tracers.run_collector import RunCollectorCallbackHandler
from langsmith import Client

work_dir = os.path.dirname(os.path.abspath((__file__)))
os.environ["WORK_DIR"] = work_dir


def _set_pages():
    dashboard = st.Page(
        "pages/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True
    )
    page_1 = st.Page("pages/page_1.py", title="광고 생성 봇", icon=":material/search:")
    page_2 = st.Page("pages/page_2.py", title="광고 심의 봇", icon=":material/history:")

    pg = st.navigation(
        {
            "Reports": [dashboard],
            "Advisor": [page_1, page_2],
        }
    )
    pg.run()


def config_langsmith():
    client = Client()
    ls_tracer = LangChainTracer(project_name=os.getenv("LANGCHAIN_PROJECT"), client=client)
    run_collector = RunCollectorCallbackHandler()
    cfg = RunnableConfig()
    cfg["callbacks"] = [ls_tracer, run_collector]
    cfg["configurable"] = {"session_id": "any"}


def _set_session_id():
    for ux in st.experimental_user.keys():
        print(f"{ux} : {st.experimental_user.get(ux)}")
        st.session_state['session_id'] = ux


if __name__ == "__main__":
    subprocess.run(["redis-server"])
    _set_pages()
    _set_session_id()
    config_langsmith()
    # redis.startup()
