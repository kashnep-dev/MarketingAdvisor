"""
@ FileName : tb_session.py
@ Description : AdCensor SESSION 로그 테이블의 스키마를 정의한다.
"""
from datetime import datetime
from typing import Dict

from sqlalchemy import Column, DateTime, String, INT, FLOAT
from sqlalchemy.ext.declarative import declarative_base
from common.model import TbSession

Base = declarative_base()


class TbSessionLog(Base):
    __tablename__ = 'tb_session'

    def __init__(self, param: TbSession):
        self.session_id = param.SESSION_ID
        self.service_id = param.SERVICE_ID
        self.user_id = param.USER_ID
        self.create_dt = param.CREATE_DT
        self.end_dt = param.END_DT
        self.duration_time = param.DURATION_TIME
        self.trace_count = param.TRACE_COUNT
        self.usage_cost = param.USAGE_COST
        self.usage_token_count = param.USAGE_TOKEN_COUNT

    session_id = Column(String, primary_key=True, nullable=False)
    service_id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, primary_key=True, nullable=False)
    create_dt = Column(DateTime, primary_key=True, nullable=True, default=datetime.now())
    end_dt = Column(DateTime, primary_key=True, nullable=True, default=datetime.now())
    duration_time = Column(INT, primary_key=True, nullable=True)
    trace_count = Column(INT, primary_key=True, nullable=True)
    usage_cost = Column(FLOAT, primary_key=True, nullable=True)
    usage_token_count = Column(INT, primary_key=True, nullable=True)

    def get_tb_name(self) -> str:
        return self.__tablename__

    def get_tb_dtype(self) -> Dict:
        dtype = dict()
        for c in self.__table__.columns:
            dtype[c.name] = c.type
        return dtype
