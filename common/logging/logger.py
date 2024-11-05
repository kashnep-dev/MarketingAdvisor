"""
@ FileName      : logger.py
@ Description   : AdCensor의 로깅 설정을 초기화한다.
                  현재 환경(APP_ENV)에 따라 적절한 로깅 설정 파일(logging.yaml)을 읽어와 로깅을 구성한다.
@ Usage Example :
    LOGGER.info("Application started")
    LOGGER.error("An error occurred")
"""

import logging.config

LOGGER = logging.getLogger("root")
