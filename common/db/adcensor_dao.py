"""
@ FileName : adcensor_dao.py
@ Description : 로그 데이터를 데이터베이스에 삽입하는 함수들을 포함한 모듈
"""
from common.db.db_connection import repository
from common.db.schemas.tb_session import TbSession
from common.db.schemas.tb_trace import TbTrace
from common.db.schemas.tb_generation import TbGeneration
from sqlalchemy.exc import IntegrityError
from common.logging.logger import LOGGER
import os


@repository
def insert_session_log(param: TbSession, db):
    """
    세션 로그를 데이터베이스에 삽입하는 함수
    param: TbSession 인스턴스
    db: 데이터베이스 세션
    """
    try:
        db.add(instance=param)
        db.flush()
    except IntegrityError as e:
        db.rollback()
        LOGGER.error(f"중복된 키가 발견되었습니다: {e}")


@repository
def insert_trace_log(param: TbTrace, db):
    """
    트레이스 로그를 데이터베이스에 삽입하는 함수
    param: TbTrace 인스턴스
    db: 데이터베이스 세션
    """
    try:
        db.add(instance=param)
        db.flush()
    except IntegrityError as e:
        db.rollback()
        LOGGER.error(f"중복된 키가 발견되었습니다: {e}")


@repository
def insert_generation_log(param: TbGeneration, db):
    """
    생성 로그를 데이터베이스에 삽입하는 함수
    param: TbGeneration 인스턴스
    db: 데이터베이스 세션
    """
    try:
        db.add(instance=param)
        db.flush()
    except IntegrityError as e:
        db.rollback()
        LOGGER.error(f"중복된 키가 발견되었습니다: {e}")


@repository
def insert_session_log_by_file(param: TbSession, file_path: str, db):
    """
    세션 로그를 데이터베이스에 삽입하는 함수
    param: TbSession 인스턴스
    db: 데이터베이스 세션
    """
    try:
        db.add(instance=param)
        db.flush()

        os.chmod(file_path, 0o777)
        # os.remove(file_path)
    except Exception as e:
        db.rollback()
        LOGGER.error(f"에러가 발생했습니다. : {e}")


@repository
def insert_trace_log_by_file(param: TbTrace, file_path: str, db):
    """
    트레이스 로그를 데이터베이스에 삽입하는 함수
    param: TbTrace 인스턴스
    db: 데이터베이스 세션
    """
    try:
        db.add(instance=param)
        db.flush()

        os.chmod(file_path, 0o777)
        # os.remove(file_path)
    except Exception as e:
        db.rollback()
        LOGGER.error(f"에러가 발생했습니다. : {e}")


@repository
def insert_generation_log_by_file(param: TbGeneration, file_path: str, db):
    """
    생성 로그를 데이터베이스에 삽입하는 함수
    param: TbGeneration 인스턴스
    db: 데이터베이스 세션
    """
    try:
        db.add(instance=param)
        db.flush()

        os.chmod(file_path, 0o777)
        # os.remove(file_path)
    except Exception as e:
        db.rollback()
        LOGGER.error(f"에러가 발생했습니다. : {e}")
