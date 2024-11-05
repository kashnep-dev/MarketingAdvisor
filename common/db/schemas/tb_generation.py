"""
@ FileName : tb_generation.py
@ Description : AdCensor GENERATION 로그 테이블의 스키마를 정의한다.
"""
from datetime import datetime
from typing import Dict

from sqlalchemy import Column, DateTime, String, INT, FLOAT, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from common.model import TbGeneration

Base = declarative_base()


class TbGenerationLog(Base):
    __tablename__ = 'tb_generation'

    def __init__(self, param: TbGeneration):
        self.generation_id = param.GENERATION_ID
        self.generation_order = param.GENERATION_ORDER
        self.generation_text = param.GENERATION_TEXT
        self.response_start_time_stream = param.RESPONSE_START_TIME_STREAM
        self.response_end_time = param.RESPONSE_END_TIME
        self.response_duration_time = param.RESPONSE_DURATION_TIME
        self.response_start_time = param.RESPONSE_START_TIME
        self.user_expose_step = param.USER_EXPOSE_STEP
        self.user_expose_text = param.USER_EXPOSE_TEXT
        self.usage_cost = param.USAGE_COST
        self.usage_token_count = param.USAGE_TOKEN_COUNT
        self.usage_model_name = param.USAGE_MODEL_NAME

    generation_id = Column(String, primary_key=True, nullable=False)
    generation_order = Column(INT, primary_key=True, nullable=False)
    generation_text = Column(String, primary_key=True, nullable=False)
    response_start_time_stream = Column(DateTime, primary_key=True, nullable=False, default=datetime.now())
    response_end_time = Column(DateTime, primary_key=True, nullable=False, default=datetime.now())
    response_duration_time = Column(INT, primary_key=True, nullable=True)
    response_start_time = Column(DateTime, primary_key=True, nullable=True, default=datetime.now())
    user_expose_step = Column(BOOLEAN, primary_key=True, nullable=True)
    user_expose_text = Column(String, primary_key=True, nullable=True)
    usage_cost = Column(FLOAT, primary_key=True, nullable=True)
    usage_token_count = Column(INT, primary_key=True, nullable=True)
    usage_model_name = Column(String, primary_key=True, nullable=True)

    def get_tb_name(self) -> str:
        return self.__tablename__

    def get_tb_dtype(self) -> Dict:
        dtype = dict()
        for c in self.__table__.columns:
            dtype[c.name] = c.type
        return dtype
