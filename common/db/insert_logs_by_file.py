import os
import pickle
from os import path
from typing import List

from common.db import adcensor_dao as dao
from common.db.db_connection import transactional
from common.db.schemas.tb_generation import TbGenerationLog
from common.db.schemas.tb_session import TbSessionLog
from common.db.schemas.tb_trace import TbTraceLog
from common.logging.logger import LOGGER


@transactional
def send_session_log_by_file():
    """
    세션 로그 파일을 읽어 DB에 저장 한다.
    """
    work_dir = os.environ['WORK_DIR']
    session_log_path = path.join(work_dir, "resources", "logs", "session")
    logs = load_logs(session_log_path)
    for tb_session in logs:
        dao.insert_session_log_by_file(TbSessionLog(tb_session), session_log_path)


@transactional
def send_generation_log_by_file():
    """
    생성 로그 파일을 읽어 DB에 저장 한다.
    """
    work_dir = os.environ['WORK_DIR']
    generation_log_path = path.join(work_dir, "resources", "logs", "generation")
    logs = load_logs(generation_log_path)
    for tb_generation in logs:
        dao.insert_generation_log_by_file(TbGenerationLog(tb_generation), generation_log_path)


@transactional
def send_trace_log_by_file():
    """
    이력 로그 파일을 읽어 DB에 저장 한다.
    """
    work_dir = os.environ['WORK_DIR']
    trace_log_path = path.join(work_dir, "resources", "logs", "trace")
    logs = load_logs(trace_log_path)
    for tb_trace in logs:
        dao.insert_trace_log_by_file(TbTraceLog(tb_trace), trace_log_path)


def load_logs(directory_path) -> List:
    logs = []
    # directory_path = path.join(os.environ["WORK_DIR"], "resources", "logs", "trace")
    entries = os.listdir(directory_path)

    # 파일 경로를 순차적으로 처리
    for entry in entries:
        file_path = os.path.join(directory_path, entry)

        if os.path.isfile(file_path):
            try:
                with open(file_path, 'rb') as f:
                    content = pickle.load(f)
                    logs.append(content)
                    LOGGER.debug(f"Reading file: {file_path}")
                    LOGGER.debug(content)  # 파일 내용을 출력 (필요에 따라 처리)
            except Exception as e:
                LOGGER.error(f"Error reading file {file_path}: {str(e)}")
    return logs
