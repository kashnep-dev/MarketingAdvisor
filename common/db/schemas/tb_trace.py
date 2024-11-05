"""
@ FileName : tb_trace.py
@ Description : AdCensor TRACE 로그 테이블의 스키마를 정의한다.
"""
from datetime import datetime
from typing import Dict

from sqlalchemy import Column, DateTime, String, INT, FLOAT, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from common.model import TbTrace

Base = declarative_base()


class TbTraceLog(Base):
    __tablename__ = 'tb_trace'

    def __init__(self, param: TbTrace):
        self.trace_id = param.TRACE_ID
        self.trace_content = param.TRACE_CONTENT
        self.trace_order = param.TRACE_ORDER
        self.session_id = param.SESSION_ID
        self.prompt_id = param.PROMPT_ID
        self.input_time = param.INPUT_TIME
        self.user_input_yn = param.USER_INPUT_YN
        self.user_input_text = param.USER_INPUT_TEXT
        self.usage_cost = param.USAGE_COST
        self.usage_token_count = param.USAGE_TOKEN_COUNT

    trace_id = Column(String, primary_key=True, nullable=False)
    trace_content = Column(String, primary_key=True, nullable=False)
    trace_order = Column(INT, primary_key=True, nullable=False)
    session_id = Column(String, primary_key=True, nullable=False)
    prompt_id = Column(String, primary_key=True, nullable=False)
    input_time = Column(DateTime, primary_key=True, nullable=True, default=datetime.now())
    user_input_yn = Column(BOOLEAN, primary_key=True, nullable=True)
    user_input_text = Column(String, primary_key=True, nullable=True)
    usage_cost = Column(FLOAT, primary_key=True, nullable=True)
    usage_token_count = Column(INT, primary_key=True, nullable=True)

    def get_tb_name(self) -> str:
        return self.__tablename__

    def get_tb_dtype(self) -> Dict:
        dtype = dict()
        for c in self.__table__.columns:
            dtype[c.name] = c.type
        return dtype
