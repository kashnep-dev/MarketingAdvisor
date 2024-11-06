from pathlib import Path

import streamlit as st

from common.util.adcensor_util import set_session_state
from service.review_adv import ReviewAdvertisement

st.title("📑 광고 심의")

for ux in st.experimental_user.keys():
    print(f"review:{st.experimental_user.get(ux)}")
    st.session_state.session_id = f"review:{st.experimental_user.get(ux)}"
    st.session_state.user_id = f"{st.experimental_user.get(ux)}"

set_session_state()

# Display chat messages from history on app rerun
for message in st.session_state.review_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.sidebar:
    review_model_name = st.selectbox(
        "분석 모델을 선택해 주세요.",
        ("gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"),
        key="model_name",
        disabled=st.session_state.is_review_streaming
    )

    review_product_type = st.radio(
        "상품유형을 선택해 주세요.",
        ["신용카드"],
        key="product_type",
        disabled=st.session_state.is_review_streaming
    )

    review_channel = st.radio(
        "발송 채널을 선택해 주세요.",
        ["LMS", "앱푸시", "Web"],
        key="channel",
        disabled=st.session_state.is_review_streaming
    )

    review_ad_text = st.text_area("광고 문구를 입력해 주세요.", key="ad_text", disabled=st.session_state.is_review_streaming)

if review_query := st.chat_input("궁금한 내용을 입력해 주세요", disabled=st.session_state.is_review_streaming):
    if not st.session_state.is_review_streaming:
        st.session_state.review_messages.append({"role": "user", "content": review_query})
        with st.chat_message("user"):
            st.session_state.is_review_streaming = True
            st.session_state.run_review_rerun = True
            st.session_state.review_query = review_query
            st.markdown(review_query)
            st.rerun()

if st.session_state.run_review_rerun:
    st.session_state.run_review_rerun = False
    with st.chat_message("assistant"):
        generator = ReviewAdvertisement(
            model_name=review_model_name,
            template_path=Path(__file__).resolve().parent.parent / "resources/prompts/review_advertisement2.yaml",
            query=st.session_state.review_query,
            session_id=st.session_state.session_id,
            service_id=st.session_state.session_id,
            user_id=st.session_state.user_id,
            channel=review_channel,
            ad_text=review_ad_text
        )
        with st.spinner('답변을 생성 중입니다...'):
            response = st.write_stream(generator.generate_stream())
        st.session_state.review_messages.append({"role": "assistant", "content": response})
        st.session_state.is_review_streaming = False
        st.rerun()
