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

    review_ad_text = st.text_area(label="광고 문구를 입력해 주세요.",
                                  value="""
                                  (광고)[신한카드, 일시불 분할납부 서비스 안내]


                                    (광고)[신한카드]
                                    
                                    
                                    고객님께서 이용하신 일시불 결제금액을 손쉽게 분할납부하실 수 있도록 안내드리오니, 필요하신 경우 신청하여 주시기 바랍니다.
                                    
                                    
                                    ■ 분할납부 신청
                                     - 아래 URL 또는 고객센터(1544-7000) 통하여 신청 가능
                                        ☞ https://shcard.io/PAnzTmf
                                    
                                    
                                    ■ 주의사항
                                     - 5만원 이상 국내/해외 일시불 거래건 분할납부 신청 가능
                                     - 국내 이용 5만원 미만 소액 거래건의 경우, 최대 10건 합산 5만원 이상 시 분할납부 신청 가능
                                     - 분할납부 신청건은 할부수수료가 적용되며, 할부수수료율은 할부개월에 따라 다르게 적용
                                     - 분할납부 신청건은 각종 무이자/슬림할부, 포인트 및 제휴카드 실적 적립 제외
                                     - 가맹점에 따라 분할납부 불가 또는 할부개월수 제한 가능 (소액 거래건 합산 신청 시 최대 6개월 가능)
                                     - 본 서비스는 당사 사정에 따라 예고없이 중단/변경 가능
                                    
                                    
                                    * 금융소비자는 금융소비자보호법 제19조 제1항에 따라 해당 금융상품 또는 서비스에 대하여 설명받을 권리가 있습니다.
                                    * 계약체결 전 카드별 연회비 등 상세사항은 상품설명서,약관 및 홈페이지 참조
                                    * 신용카드 발급이 부적정한 경우(개인신용평점 낮음, 연체(단기 포함) 사유 발생 등), 카드발급이 제한될 수 있음
                                    * 카드 이용대금(수수료 포함)은 고객님 결제일에 상환하여야 함
                                    ※ 상환능력 대비 신용카드 사용액 과도시, 개인신용평점 하락할 수 있음
                                    ※ 개인신용평점 하락시, 금융거래 관련 불이익 발생할 수 있음
                                    ※ 일정기간 연체시, 모든 이용대금 변제 의무 발생할 수 있음
                                    준법감시 심의필 제20240617-Cpc-008호(2024.06.17~2025.06.16)
                                    * 수신거부 080-800-8114(무료)
                                  """,
                                  height=500, key="ad_text", disabled=st.session_state.is_review_streaming)

if review_query := st.chat_input("다음 광고 문구를 심의해 주세요", disabled=st.session_state.is_review_streaming):
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
