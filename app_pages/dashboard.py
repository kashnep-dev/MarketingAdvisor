import os
import sqlite3
from datetime import datetime, timedelta, date
import subprocess
import streamlit as st
from streamlit_echarts import st_echarts
import pandas as pd
from typing import Optional, Dict
from common.util.redis_connection import redis_connection_pool as redis
import asyncio
st.title("📊 Dashboard")

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


class DrawLineChart:
    def __init__(self, date_tuple):
        self.start_date: date = date_tuple[0]
        self.end_date: date = date_tuple[1]
        self.date_format: str = "%Y-%m-%d"
        self.start_date_str = self.end_date_str = Optional[str]
        self.token_dict = self.cost_dict = Optional[Dict[str, float]]

    def generate_date_range(self, date_format):
        return [(self.start_date + timedelta(days=i)).strftime(date_format)
                for i in range((self.end_date - self.start_date).days + 1)]

    def retrieve_linechart_data(self):
        # SQLite 데이터베이스 연결 및 데이터 가져오기
        conn = sqlite3.connect(os.path.join(os.environ["WORK_DIR"], "shcard.db"))
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT DATE(INPUT_TIME) AS DATE,
                   SUM(USAGE_COST) * 100 AS TOTAL_USAGE_COST,
                   SUM(USAGE_TOKEN_COUNT) / 1000.0 AS TOTAL_USAGE_TOKEN_COUNT
            FROM TB_TRACE
            WHERE INPUT_TIME BETWEEN DATE('{self.start_date_str}') AND DATE('{self.end_date_str}')
            GROUP BY DATE(INPUT_TIME)
            ORDER BY DATE
        """)
        rows = cursor.fetchall()
        conn.close()
        for date_str, total_usage_cost, total_usage_token_count in rows:
            self.token_dict[date_str] = total_usage_token_count
            self.cost_dict[date_str] = total_usage_cost

    def draw(self):
        category_days = self.generate_date_range(self.date_format)
        short_category_days = self.generate_date_range(self.date_format[3:])

        # 조회 기간 설정
        self.start_date_str, end_date_str = category_days[0], category_days[-1]
        self.end_date_str = (today + timedelta(days=1)).strftime(self.date_format) if today.strftime(self.date_format) == end_date_str else end_date_str

        # 초기값 설정
        self.token_dict = dict.fromkeys(category_days, 0)
        self.cost_dict = dict.fromkeys(category_days, 0)

        # 데이터 조회
        self.retrieve_linechart_data()

        options = {
            "title": {"text": "사용 정보"},
            "tooltip": {"trigger": "axis"},
            "legend": {"data": ["토큰 사용량(k)", "사용 비용(¢)"]},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "toolbox": {},
            "xAxis": {
                "type": "category",
                "boundaryGap": True,
                "data": short_category_days,
            },
            "yAxis": {"type": "value"},
            "series": [
                {
                    "name": "토큰 사용량(k)",
                    "type": "line",
                    "stack": "총량",
                    "data": list(self.token_dict.values()),
                },
                {
                    "name": "사용 비용(¢)",
                    "type": "bar",
                    "stack": "총량",
                    "data": list(self.cost_dict.values()),
                },
            ]
        }

        # 차트 렌더링
        st_echarts(options=options, height="400px")


if search_button:
    if len(date_inputs) > 1:
        line_chart = DrawLineChart(date_tuple=date_inputs)
        line_chart.draw()
        print(f"search_button : {search_button}")


def parse_df_h(output):
    headers = output[0].split()
    rows = [line.split() for line in output[1:]]

    # 각 행의 길이를 확인하고 부족한 열이 있으면 빈 문자열 추가
    adjusted_rows = []
    for row in rows:
        # 6개의 항목만 있는 경우 마지막 열 추가
        if len(row) == 6:
            row.append("")
        adjusted_rows.append(row)

    # DataFrame 생성
    df = pd.DataFrame(adjusted_rows, columns=headers)

    # DataFrame 출력
    return df


if os.name == 'posix':  # UNIX 계열 운영 체제 확인
    pwd = subprocess.run("pwd", shell=True, capture_output=True, text=True).stdout.strip()
    ls_al = subprocess.run(["ls", "-al"], capture_output=True, text=True).stdout.splitlines()
    df_h = subprocess.run(["df", "-h"], capture_output=True, text=True).stdout.splitlines()

    st.code(f"{pwd} : {"\n".join(ls_al)}", language="bash")
    st.dataframe(parse_df_h(df_h))


key_sizes = redis.get_redis_keys_and_sizes()
for key, size in key_sizes.items():
    st.info(f"Key: {key}, Size: {size}")

redis_key = st.text_input("삭제할 키를 입력해 주세요.")
delete_button = st.button("삭제")
if delete_button:
    asyncio.run(redis.remove(redis_key))
