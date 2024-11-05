"""
@ FileName : exception_handler.py
@ Description : exception 발생 시 각 exception class에 따라 적절한 return 값을 생성하여 반환한다.
                - HTTPException -> http_exception_handler
                - Exception, ExceptionGroup, BizException, SystemException -> exception_handler
"""
from exceptiongroup import ExceptionGroup
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from common import message as messages
from common.exception.exception_model import SystemException, BizException


async def exception_handler(request: Request, exc: Exception):
    # SystemException과 BizException이 아닌 기타 Exception일 경우
    # SystemException의 기본 설정값을 적용함
    sys_exc = SystemException()
    code = sys_exc.status_code
    message = sys_exc.message
    send = sys_exc.send

    # ExceptionGroup일 경우 최종 Exception만 추출
    if isinstance(exc, ExceptionGroup):
        exc = exc.exceptions[-1]

    # SystemException이나 BizException일 경우
    # 실제 exception의 설정값을 적용함
    if isinstance(exc, (BizException, SystemException)):
        code = exc.status_code
        message = exc.message
        send = exc.send

    result = {
        'status': {
            'code': code,
            'message': message
        },
        'data': {}
    }

    # streaming일 경우 (send is not None)
    if send:
        await send(str(result))

    return JSONResponse(
        status_code=code,
        content=result
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    # LOGGER.warning("http_exception_handler: %s", traceback.format_exc())
    code = getattr(exc, "status_code", status.HTTP_200_OK)
    try:
        message = exc.detail
    except:
        message = messages.HTTP_ERROR

    result = {
        'status': {
            'code': code,
            'message': message
        },
        'data': {}
    }

    return JSONResponse(
        status_code=code,
        content=result
    )
