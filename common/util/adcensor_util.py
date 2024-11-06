"""
@ FileName : adcensor_util
@ Description : AdCensor에 필요한 util 함수를 정의한다.
"""

from typing import Optional

import streamlit as st
import tiktoken
from langchain_community.chat_message_histories import RedisChatMessageHistory

from common.util.redis_connection import redis_connection_pool as redis

# 1,000 토큰당 OpenAI 모델의 입력 토큰과 출력 토큰의 비용을 각각 정의함
MODEL_COST_PER_1K_TOKENS = {
    # GPT-4o input
    "gpt-4o": 0.0025,
    "gpt-4o-2024-05-13": 0.005,
    "gpt-4o-2024-08-06": 0.0025,
    # GPT-4o output
    "gpt-4o-completion": 0.01,
    "gpt-4o-2024-05-13-completion": 0.015,
    "gpt-4o-2024-08-06-completion": 0.01,

}

MODEL_COST_PER_IMAGE = {
    # dall-e-3
    "dall-e-3-standard-1024×1024": 0.040,
    "dall-e-3-standard-1024×1792": 0.080,
    "dall-e-3-standard-1792×1024": 0.080,
    "dall-e-3-hd-1024×1024": 0.080,
    "dall-e-3-hd-1024×1792": 0.120,
    "dall-e-3-hd-1792×1024": 0.120,

    # dall-e-2
    "dall-e-2-standard-1024×1024": 0.020,
    "dall-e-2-standard-512×512": 0.018,
    "dall-e-2-standard-256×256": 0.016
}


def standardize_model_name(
        model_name: str,
        is_completion: bool = False,
) -> str:
    """
    Standardize the model name to a format that can be used in the OpenAI API.

    Args:
        model_name: Model name to standardize.
        is_completion: Whether the model is used for completion or not.
            Defaults to False.

    Returns:
        Standardized model name.

    """
    model_name = model_name.lower()
    if ".ft-" in model_name:
        model_name = model_name.split(".ft-")[0] + "-azure-finetuned"
    if ":ft-" in model_name:
        model_name = model_name.split(":")[0] + "-finetuned-legacy"
    if "ft:" in model_name:
        model_name = model_name.split(":")[1] + "-finetuned"
    if is_completion and (
            model_name.startswith("gpt-4")
            or model_name.startswith("gpt-3.5")
            or model_name.startswith("gpt-35")
            or model_name.startswith("o1-")
            or ("finetuned" in model_name and "legacy" not in model_name)
    ):
        return model_name + "-completion"
    else:
        return model_name


def get_openai_token_cost_for_model(model_name: str, num_tokens: int, is_completion: bool = False) -> float:
    """
    Get the cost in USD for a given model and number of tokens.

    Args:
        model_name: Name of the model
        num_tokens: Number of tokens.
        is_completion: Whether the model is used for completion or not.
            Defaults to False.

    Returns:
        Cost in USD.
    """
    model_name = standardize_model_name(model_name, is_completion=is_completion)
    if model_name not in MODEL_COST_PER_1K_TOKENS:
        raise ValueError(
            f"Unknown model: {model_name}. Please provide a valid OpenAI model name."
            "Known models are: " + ", ".join(MODEL_COST_PER_1K_TOKENS.keys())
        )
    return MODEL_COST_PER_1K_TOKENS[model_name] * (num_tokens / 1000)


def get_openai_image_cost_for_model(model: str, quality: str, n: int = 1, size: str = "1024x1024") -> float:
    """
    주어진 DALL-E 모델이 생성한 이미지에 대한 비용을 계산.

        Args:
            model (str): 이미지 생성 모델 이름 (예: "dall-e-3", "dall-e-2").
            quality (str): 이미지 생성 품질 (예: "hd", "standard").
            n (int): 생성한 이미지 갯수.
            size (str): 생성된 이미지의 해상도.

        Returns:
            float: 주어진 이미지의 생성 정보에 따른 총 비용.

        Raises:
            ValueError: 올바르지 않은 모델 이름이 제공된 경우.
    """
    model_name = f"{model}-{quality}-{size}"
    if model_name not in MODEL_COST_PER_IMAGE:
        raise ValueError(f"Unknown model: {model_name}. Please provide a valid OpenAI model name."
                         "Known models are: " + ", ".join(MODEL_COST_PER_IMAGE.keys()))
    else:
        return MODEL_COST_PER_IMAGE[model_name] * n


def get_token_size(text: str, model_name: str) -> int:
    """
    문장을 토큰화하여 토큰 수를 반환한다.

    Args:
        text (str): 질의, 프롬프트, 생성 결과 등
        model_name (str): 모델명

    Returns:
        int: 입력된 텍스트의 토큰 수
    """
    encoder = tiktoken.encoding_for_model(model_name)
    tokens = encoder.encode(text)
    return len(tokens)


def chat_history(history_list) -> list:
    """
        주어진 채팅 메시지 목록을 역할과 내용으로 구성된 list 형태로 변환.

        Args:
            history_list (list): "역할: 내용" 형식의 채팅 메시지 목록 (예: ["user: 안녕하세요!", "assistant: 안녕하세요!"]).

        Returns:
            list: 각 메시지를 (역할, 내용) 튜플 형태로 변환한 리스트.
        """
    history = []
    for message in history_list:
        role, content = message.split(": ", 1)
        history.append((role, content))
    return history


def get_message_history(session_id: str, memory_window_size: int) -> RedisChatMessageHistory:
    history = RedisChatMessageHistory(session_id, url=redis.get_url())

    history_list = history.messages[-memory_window_size:]
    if len(history_list) % 2 != 0:
        history_list = history_list[1:]

    history.clear()
    for idx in range(0, len(history_list), 2):
        history.add_user_message(history_list[idx].content)
        history.add_ai_message(history_list[idx + 1].content)

    return history


def set_session_state():
    if "generate_messages" not in st.session_state:
        st.session_state.generate_messages = []

    if "review_messages" not in st.session_state:
        st.session_state.review_messages = []

    if 'is_review_streaming' not in st.session_state:
        st.session_state.is_review_streaming = False

    if 'is_generate_streaming' not in st.session_state:
        st.session_state.is_generate_streaming = False

    if 'run_generate_rerun' not in st.session_state:
        st.session_state.run_generate_rerun = False

    if 'run_review_rerun' not in st.session_state:
        st.session_state.run_review_rerun = False

    if 'generate_query' not in st.session_state:
        st.session_state.generate_query = Optional[str]

    if 'review_query' not in st.session_state:
        st.session_state.review_query = Optional[str]