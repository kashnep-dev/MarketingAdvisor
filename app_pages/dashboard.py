import os
import sqlite3
from datetime import datetime, timedelta
import subprocess
import streamlit as st
from streamlit_echarts import st_echarts
import pandas as pd

st.title("📊 Dashboard")

# 날짜 범위 설정
today = datetime.today()
a_week_ago = today - timedelta(days=7)

# 날짜 선택 입력
date_inputs = st.date_input(
    "조회 날짜를 선택해 주세요.",
    (a_week_ago, today),
    min_value=a_week_ago,
    max_value=today,
    format="YYYY-MM-DD",
)


# 주어진 날짜 범위의 날짜 목록 생성
def generate_date_range(start_date, end_date, date_format="%Y-%m-%d"):
    return [(start_date + timedelta(days=i)).strftime(date_format)
            for i in range((end_date - start_date).days + 1)]


category_days = generate_date_range(date_inputs[0], date_inputs[1])
short_category_days = generate_date_range(date_inputs[0], date_inputs[1], date_format="%m-%d")

# 조회 기간 설정
start_date_str, end_date_str = category_days[0], category_days[-1]
end_date_str = (today + timedelta(days=1)).strftime('%Y-%m-%d') if today.strftime('%Y-%m-%d') == end_date_str else end_date_str

# 초기값 설정
token_dict = dict.fromkeys(category_days, 0)
cost_dict = dict.fromkeys(category_days, 0)

# SQLite 데이터베이스 연결 및 데이터 가져오기
conn = sqlite3.connect(os.path.join(os.environ["WORK_DIR"], "shcard.db"))
cursor = conn.cursor()
cursor.execute(f"""
    SELECT DATE(INPUT_TIME) AS DATE,
           SUM(USAGE_COST) * 100 AS TOTAL_USAGE_COST,
           SUM(USAGE_TOKEN_COUNT) / 1000.0 AS TOTAL_USAGE_TOKEN_COUNT
    FROM TB_TRACE
    WHERE INPUT_TIME BETWEEN DATE('{start_date_str}') AND DATE('{end_date_str}')
    GROUP BY DATE(INPUT_TIME)
    ORDER BY DATE
""")
rows = cursor.fetchall()

# 데이터 업데이트
for date, total_usage_cost, total_usage_token_count in rows:
    token_dict[date] = total_usage_token_count
    cost_dict[date] = total_usage_cost

# 그래프 옵션 설정
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
            "data": list(token_dict.values()),
        },
        {
            "name": "사용 비용(¢)",
            "type": "bar",
            "stack": "총량",
            "data": list(cost_dict.values()),
        },
    ],
}

# 차트 렌더링
st_echarts(options=options, height="400px")

# 데이터베이스 연결 종료
conn.close()


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


du_sh = subprocess.run(["du", "-sh", "../"], shell=True, capture_output=True, text=True).stdout.splitlines()
pwd = subprocess.run("pwd", shell=True, capture_output=True, text=True).stdout.strip()
ls_al = subprocess.run(["ls", "-al"], capture_output=True, text=True).stdout.splitlines()
df_h = subprocess.run(["df", "-h"], capture_output=True, text=True).stdout.splitlines()


st.info(f"pwd : {pwd}")
st.code(f"{"\n".join(du_sh)}", language="bash")
st.code(f"{"\n".join(ls_al)}", language="bash")
st.dataframe(parse_df_h(df_h))
