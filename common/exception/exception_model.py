"""
@ FileName : exception_model
@ Description : Exception class를 정의한다.
                - SystemException
                - BizException
                각 Exception class는 다음과 같은 멤버 변수를 포함한다.
                1) status_code = 상태코드
                2) message = 에러 메시지 내용
                3) send = Non-Streaming일 경우 None, Streaming일 경우 Sender 객체
"""

from common.model import Sender
from typing import Union
from common import message


class SystemException(Exception):
    """프로젝트의 비영업적 예외 발생 시 사용하는 클래스"""

    def __init__(
            self,
            code: int = 500,
            message: str = message.SERVER_ERROR,
            send: Union[None, Sender] = None
    ):
        self.status_code = code
        self.message = message
        self.send = send


class BizException(Exception):
    """프로젝트의 업무처리 중 발생되는 예외를 위한 클래스"""

    def __init__(
            self,
            code: int = 400,
            message: str = "",
            send: Union[None, Sender] = None
    ):
        self.status_code = code
        self.message = message
        self.send = send
