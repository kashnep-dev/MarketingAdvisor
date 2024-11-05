"""
@ FileName : model
@ Description : AdCensor에서 사용할 모델을 정의 한다.
"""
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, Union, Optional
from pydantic import BaseModel, Field

Sender = Callable[[Union[str, bytes, Dict]], Awaitable[None]]


class TbSession(BaseModel):
    """ 세션 로그 정보 """

    SESSION_ID: str = Field(..., description="VARCHAR(50)	uuid	사용자 채팅 세션 식별자, 생성 규칙은 미확정")
    SERVICE_ID: str = Field(..., description="VARCHAR(50)	uuid	사용자 채팅 서비스 식별자, 생성 규칙은 미확정")
    USER_ID: str = Field(..., description="VARCHAR(50)	uuid	사용자 식별자, 생성 규칙은 미확정")
    CREATE_DT: datetime = Field(..., description="생성 일시 TIMESTAMP	2024-09-24 14:35:23")
    END_DT: datetime = Field(..., description="종료 일시 TIMESTAMP	2024-09-24 14:40:23")
    DURATION_TIME: int = Field(..., description="유지 시간	INT	300	세션 유지 시간 (초)")
    TRACE_COUNT: int = Field(..., description="Trace 카운트	INT	3	해당 세션에서 입력된 Trace 개수")
    USAGE_COST: float = Field(..., description="사용비용(trace+gen) (USD)	INT	7.2")
    USAGE_TOKEN_COUNT: int = Field(..., description="사용토큰수(trace+gen)	INT	120")


class TbTrace(BaseModel):
    TRACE_ID: str = Field(..., description="Trace id	VARCHAR(50)	uuid	LLM 입력 텍스트 식별자, 생성 규칙은 미확정")
    TRACE_CONTENT: str = Field(...,
                               description="Trace content	TEXT	NoSQL에 저장	LLM에 입력되는 텍스트 (사용자 직접 입력 단계 시, 프롬프트+직접 입력한 질문), 생성 규칙은 미확정")
    TRACE_ORDER: int = Field(..., description="Trace order	INT	2	세션별 입력 순서")
    SESSION_ID: str = Field(..., description="세션 id	VARCHAR(50)	uuid	사용자 채팅 세션 식별자, 생성 규칙은 미확정")
    PROMPT_ID: str = Field(...,
                           description="프롬프트 id	VARCHAR(50)	uuid	입력에 사용된 프롬프트 식별자, 프롬프트 테이블에서 참조한 것이 아니라 직접 작성한 경우 null")
    INPUT_TIME: datetime = Field(..., description="입력시점	TIMESTAMP	2024-09-24 14:35:23	")
    USER_INPUT_YN: bool = Field(...,
                                description="사용자가 직접 입력한 질문인지 여부	BOOLEAN	True	사용자 직접 입력 vs 로직상 입력되는 텍스트 구분")
    USER_INPUT_TEXT: str = Field(...,
                                 description="사용자가 직접 입력한 질문(텍스트)	TEXT	경조사 화환 신청 절차는?	직접 입력한 경우에만 해당 텍스트 있음, 없으면 NULL")
    USAGE_COST: float = Field(..., description="사용비용 (USD)	INT	60	아래에서 추출한 토큰 수 * 토큰 당 비용 계산 산식으로 산출")
    USAGE_TOKEN_COUNT: int = Field(..., description="사용토큰수	INT	3.6	response json에서 해당 항목 추출")


class TbTraceNoSQL(BaseModel):
    SESSION_ID: str = Field(..., description="VARCHAR(50)	uuid	사용자 채팅 세션 식별자, 생성 규칙은 미확정")
    SERVICE_ID: str = Field(..., description="VARCHAR(50)	uuid	사용자 채팅 서비스 식별자, 생성 규칙은 미확정")
    TRACE_ID: str = Field(..., description="Trace id	VARCHAR(50)	uuid	LLM 입력 텍스트 식별자, 생성 규칙은 미확정")
    TRACE_CONTENT: str = Field(...,
                               description="Trace content	TEXT	NoSQL에 저장	LLM에 입력되는 텍스트 (사용자 직접 입력 단계 시, 프롬프트+직접 입력한 질문), 생성 규칙은 미확정")
    GENERATION: dict = Field(..., description="generation_id, generation_content")


class TbGeneration(BaseModel):
    GENERATION_ID: str = Field(..., description="Generation id	VARCHAR(50)	uuid	LLM 답변 식별자, 생성 규칙은 미확정")
    GENERATION_ORDER: int = Field(..., description="Generation order	INT		세션별 생성 순서, 생성 규칙은 미확정")
    GENERATION_TEXT: str = Field(..., description="Generation	TEXT	NoSQL에 저장	LLM이 생성한 답변")
    RESPONSE_START_TIME_STREAM: datetime = Field(...,
                                                 description="답변시작시점 (스트림)	TIMESTAMP	2024-09-24 14:41:23	실제 서비스에서 스트림 반환이 될지는 미확정, 불가시 로깅 안함")
    RESPONSE_END_TIME: datetime = Field(...,
                                        description="답변종료시점 (스트림)	TIMESTAMP	2024-09-24 14:41:50	실제 서비스에서 스트림 반환이 될지는 미확정, 불가시 로깅 안함")
    RESPONSE_DURATION_TIME: int = Field(...,
                                        description="답변소요시간 (스트림) (초)	INT	27	실제 서비스에서 스트림 반환이 될지는 미확정, 불가시 로깅 안함")
    RESPONSE_START_TIME: datetime = Field(..., description="답변시작시점 (스트림X)	TIMESTAMP	2024-09-24 14:41:23	")
    USER_EXPOSE_STEP: bool = Field(...,
                                   description="사용자에게 노출되는 Generation 단계인지 여부	BOOLEAN	TRUE	사용자 노출답변 vs 로직상 생성되는 텍스트 구분")
    USER_EXPOSE_TEXT: str = Field(...,
                                  description="사용자에게 노출되는 Generation (텍스트)	TEXT	인사팀 ~에게 문의하면 됩니다	사용자에게 노출된 답변인 경우에만 해당 텍스트 있음, 없으면 NULL")
    USAGE_COST: float = Field(..., description="사용비용 (USD)	INT	3.6	아래에서 추출한 토큰 수 * 토큰 당 비용 계산 산식으로 산출")
    USAGE_TOKEN_COUNT: int = Field(..., description="사용토큰수	INT	3.6	response json에서 해당 항목 추출")
    USAGE_MODEL_NAME: str = Field(..., description="사용모델명	TEXT	gpt-4o	")


class TbGenerationNoSQL(BaseModel):
    SESSION_ID: str = Field(..., description="VARCHAR(50)	uuid	사용자 채팅 세션 식별자, 생성 규칙은 미확정")
    SERVICE_ID: str = Field(..., description="VARCHAR(50)	uuid	사용자 채팅 서비스 식별자, 생성 규칙은 미확정")
    USER_ID: str = Field(..., description="user_id")
    TRACE_ID: str = Field(..., description="Trace id	VARCHAR(50)	uuid	LLM 입력 텍스트 식별자, 생성 규칙은 미확정")
    TRACE_CONTENT: str = Field(...,
                               description="Trace content	TEXT	NoSQL에 저장	LLM에 입력되는 텍스트 (사용자 직접 입력 단계 시, 프롬프트+직접 입력한 질문), 생성 규칙은 미확정")
    GENERATION: dict = Field(..., description="generation_id, generation_content")
