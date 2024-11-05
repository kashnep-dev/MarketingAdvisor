"""
@ FileName: environment.py
@ Description: 환경 변수를 관리하고 로드하는 클래스 정의 파일로
               애플리케이션 실행 환경에 따라 필요한 환경 변수를 `.env` 파일에서 로드한다.
"""
import os
from os import path

from dotenv import load_dotenv


class Environment:
    """
    환경 변수 관리 클래스.

    APP_ENV 환경 변수에 따라 설정 파일(storage.env, engine.env)을 로드한다.

    Attributes:
        없음 (모든 동작은 클래스 생성자와 정적 메서드를 통해 처리됨.)
    """

    def __init__(self):
        """
        Environment 클래스의 생성자.

        애플리케이션의 작업 디렉터리를 기준으로 APP_ENV에 따른 환경 설정 파일을 로드한다.

        Raises:
            ValueError: APP_ENV가 'dev' 또는 'prod'가 아닌 경우 예외를 발생시킴.
        """
        work_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        db_env = path.join(work_dir, "resources", "config", "dev", "storage.env")
        engine_env = path.join(work_dir, "resources", "config", "dev", "engine.env")

        load_dotenv(db_env)
        load_dotenv(engine_env)

    @staticmethod
    def get(key):
        """
        환경 변수 값을 반환한다.

        Args:
            key (str): 반환할 환경 변수의 이름.

        Returns:
            str: 요청한 환경 변수의 값.

        Raises:
            KeyError: 요청한 환경 변수가 존재하지 않는 경우 예외를 발생시킴.
        """
        return os.environ[key]


# Environment 인스턴스를 생성하여 애플리케이션 시작 시 환경 변수를 로드
env = Environment()
