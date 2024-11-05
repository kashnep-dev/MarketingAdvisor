import streamlit as st
from service.generate_adv import AdvertisementGenerator
import json
from pathlib import Path
from typing import Dict, Any

from pydantic import BaseModel

from common.logging.logger import LOGGER
from service.generate_adv import AdvertisementGenerator
from service.review_adv import ReviewAdvertisement

st.title("💡 광고 생성")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.sidebar:
    model_name = st.selectbox(
        "분석 모델을 선택해주세요.",
        ("gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"),
    )

    product_type = st.radio(
        "상품유형을 선택해주세요.",
        ("신용카드"),
    )

    channel = st.radio(
        "발송 채널을 선택해주세요.",
        ("LMS", "앱푸시", "Web"),
    )

    generate_image = st.checkbox("이미지 생성 여부")

query = st.chat_input("궁금한 내용을 입력해 주세요")

if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("assistant"):
        generator = AdvertisementGenerator(
            model_name=model_name,
            template_path=Path(__file__).resolve().parent.parent / "resources/prompts/ux_writing_guide.yaml",
            query=query,
            session_id=st.session_state["session_id"],
            service_id="service_id_001",
            user_id="kashnep",
            channel=channel
        )
        response = st.write_stream(generator.generate_stream())
        st.session_state.messages.append({"role": "assistant", "content": response})
        if generate_image:
            st.markdown(generator.generate_image(response), unsafe_allow_html=True)

