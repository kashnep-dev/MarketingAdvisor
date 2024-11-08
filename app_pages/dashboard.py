import os
import subprocess
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from common.util.adcensor_util import DrawChart

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


if search_button:
    if len(date_inputs) > 1:
        draw_chart = DrawChart(date_tuple=date_inputs, today=today)
        st.markdown("<h3>Open AI API 사용량</h2>", unsafe_allow_html=True)
        draw_chart.draw_line_chart()
        st.divider()
        print(f"search_button : {search_button}")

    if os.name == 'posix':  # UNIX 계열 운영 체제 확인
        pwd = subprocess.run("pwd", shell=True, capture_output=True, text=True).stdout.strip()
        ls_al = subprocess.run(["ls", "-al"], capture_output=True, text=True).stdout.splitlines()
        df_h = subprocess.run(["df", "-h"], capture_output=True, text=True).stdout.splitlines()

        st.markdown("<h3>Streamlit 서버 정보</h2>", unsafe_allow_html=True)
        st.code(f"{pwd} : {"\n".join(ls_al)}", language="bash")
        st.dataframe(parse_df_h(df_h))
        st.divider()


