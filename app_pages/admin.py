import asyncio
from datetime import datetime, timedelta

import streamlit as st

from common.util.adcensor_util import DrawChart
from common.util.redis_connection import redis_connection_pool as redis
import os
import sqlite3

st.title("🛡️ Admin")

st.markdown(
    """
    <style>
    .button-container {
        display: flex;
        align-items: center;
        margin-top: 27px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 날짜 범위 설정
today = datetime.today()
a_week_ago = today - timedelta(days=7)
col1, col2 = st.columns([4, 1])
with col1:
    date_inputs = st.date_input(
        "조회 날짜를 선택해 주세요.",
        (a_week_ago, today),
        min_value=(today - timedelta(days=365)),
        max_value=today,
        format="YYYY-MM-DD",
    )

with col2:
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    search_button = st.button("조회", key="search")
    st.markdown('</div>', unsafe_allow_html=True)

query_input = st.text_input("쿼리를 입력해 주세요")

if search_button:
    if len(date_inputs) > 1:
        draw_chart = DrawChart(date_tuple=date_inputs, today=today)
        st.markdown("<h3>Open AI API 사용량</h2>", unsafe_allow_html=True)
        draw_chart.draw_pie_chart()
        st.divider()

    st.markdown("<h3>Redis Key 현황</h2>", unsafe_allow_html=True)
    key_sizes = redis.get_redis_keys_and_sizes()
    for key, size in key_sizes.items():
        st.info(f"Key: {key}, Size: {size}")

    redis_key = st.text_input("삭제할 키를 입력해 주세요.")
    delete_button = st.button("삭제")
    if delete_button:
        asyncio.run(redis.remove(redis_key))

    if query_input:
        conn = sqlite3.connect(os.path.join(os.environ["WORK_DIR"], "shcard.db"))
        cursor = conn.cursor()
        cursor.execute(query_input)
        rows = cursor.fetchall()
        st.code(rows, language="sql")
        conn.close()
