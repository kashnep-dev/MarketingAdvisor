from pathlib import Path

import streamlit as st

from common.util.adcensor_util import set_session_state
from service.generate_adv import AdvertisementGenerator

st.title("💡 광고 생성")

for ux in st.experimental_user.keys():
    print(f"generate:{st.experimental_user.get(ux)}")
    st.session_state.session_id = f"generate:{st.experimental_user.get(ux)}"
    st.session_state.user_id = f"{st.experimental_user.get(ux)}"

set_session_state()

# Display chat messages from history on app rerun
for message in st.session_state.generate_messages:
    with st.chat_message(message["role"]):
        if 'img' in message["content"]:
            st.markdown(message["content"], unsafe_allow_html=True)
        else:
            st.markdown(message["content"])

with st.sidebar:
    generate_model_name = st.selectbox(
        "분석 모델을 선택해 주세요.",
        ("gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"),
        key="model_name",
        disabled=st.session_state.is_generate_streaming
    )

    generate_product_type = st.radio(
        "상품유형을 선택해 주세요.",
        ["신용카드"],
        key="product_type",
        disabled=st.session_state.is_generate_streaming
    )

    generate_channel = st.radio(
        "발송 채널을 선택해 주세요.",
        ["LMS", "앱푸시", "Web"],
        key="channel",
        disabled=st.session_state.is_generate_streaming
    )

    generate_image = st.checkbox("이미지 생성 여부",
                                 key="generate_image",
                                 disabled=st.session_state.is_generate_streaming)

if generate_query := st.chat_input("궁금한 내용을 입력해 주세요", disabled=st.session_state.is_generate_streaming):
    if not st.session_state.is_generate_streaming:
        st.session_state.generate_messages.append({"role": "user", "content": generate_query})
        with st.chat_message("user"):
            st.session_state.is_generate_streaming = True
            st.session_state.run_generate_rerun = True
            st.session_state.generate_query = generate_query
            st.markdown(generate_query)
            st.rerun()

if st.session_state.run_generate_rerun:
    st.session_state.run_generate_rerun = False
    with st.chat_message("assistant"):
        generator = AdvertisementGenerator(
            model_name=generate_model_name,
            template_path=Path(__file__).resolve().parent.parent / "resources/prompts/ux_writing_guide2.yaml",
            query=st.session_state.generate_query,
            session_id=st.session_state.session_id,
            service_id=st.session_state.session_id,
            user_id=st.session_state.user_id,
            channel=generate_channel
        )
        with st.spinner('광고 문구를 생성 중입니다...'):
            response = st.write_stream(generator.generate_stream())
        st.session_state.generate_messages.append({"role": "assistant", "content": response})
        if generate_image:
            print(generate_image)
            with st.spinner('광고 시안을 생성 중입니다...'):
                # st.markdown(f"<img src='{generator.generate_image(response)}'/>", unsafe_allow_html=True)
                img_url = generator.generate_image(response)
                st.image(img_url)
                st.session_state.generate_messages.append({"role": "assistant", "content": f"<img src='{img_url}'/>"})
        st.session_state.is_generate_streaming = False
        st.rerun()
