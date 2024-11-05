from pathlib import Path

import streamlit as st

from service.review_adv import ReviewAdvertisement

st.markdown("""
<style>
    .stApp[data-teststate=running] .stChatInput textarea,
    .stApp[data-test-script-state=running] .stChatInput textarea {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

st.title("📑 광고 심의")

for ux in st.experimental_user.keys():
    print(f"{ux} : {st.experimental_user.get(ux)}")
    st.session_state['session_id'] = f"review:{st.experimental_user.get(ux)}"

if "messages" not in st.session_state:
    st.session_state.messages = []

if 'is_streaming' not in st.session_state:
    st.session_state.is_streaming = False

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.sidebar:
    model_name = st.selectbox(
        "분석 모델을 선택해 주세요.",
        ("gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"),
        key="model_name",
        disabled=st.session_state.is_streaming
    )

    product_type = st.radio(
        "상품유형을 선택해 주세요.",
        ["신용카드"],
        key="product_type",
        disabled=st.session_state.is_streaming
    )

    channel = st.radio(
        "발송 채널을 선택해 주세요.",
        ["LMS", "앱푸시", "Web"],
        key="channel",
        disabled=st.session_state.is_streaming
    )

    ad_text = st.text_area("광고 문구를 입력해 주세요.", key="ad_text", disabled=st.session_state.is_streaming)

if query := st.chat_input("궁금한 내용을 입력해 주세요", disabled=st.session_state.is_streaming, key="query"):
    if not st.session_state.is_streaming:
        st.session_state.messages.append({"role": "user", "content": st.session_state.query})
        with st.chat_message("user"):
            st.session_state.is_streaming = True
            st.markdown(query)
            # st.rerun()
    print(st.session_state["session_id"])
    with st.chat_message("assistant"):
        generator = ReviewAdvertisement(
            model_name=model_name,
            template_path=Path(__file__).resolve().parent.parent / "resources/prompts/review_advertisement2.yaml",
            query=st.session_state.query,
            session_id=st.session_state["session_id"],
            service_id="service_id_001",
            user_id="kashnep",
            channel=channel,
            ad_text=ad_text
        )

        response = st.write_stream(generator.generate_stream())
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.is_streaming = False
        st.rerun()
