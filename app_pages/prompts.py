import streamlit as st
import pandas as pd
from langchain_core.prompts import load_prompt
import numpy as np
import os

st.title("🤖 prompts")

st.markdown("<h3>생성 시스템 프롬프트</h2>", unsafe_allow_html=True)
ux_writing_guide = load_prompt(os.path.join(os.environ["WORK_DIR"], "resources", "prompts", "ux_writing_guide.yaml"), encoding="utf-8").format()
st.markdown(f"```{ux_writing_guide}```")

st.markdown("<h3>심의 시스템 프롬프트</h2>", unsafe_allow_html=True)
review_system_prompt = load_prompt(os.path.join(os.environ["WORK_DIR"], "resources", "prompts", "review_advertisement2.yaml"), encoding="utf-8").format()
st.markdown(f"```{review_system_prompt}```")

st.markdown("<h3>생성/심의 체크리스트</h2>", unsafe_allow_html=True)
df = pd.read_excel(os.path.join(os.environ["WORK_DIR"], "resources", "checklist", "checklist_26.xlsx"))
st.dataframe(df)
