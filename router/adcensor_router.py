# import json
# from pathlib import Path
# from typing import Dict, Any
#
# from fastapi import APIRouter
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel
# from sse_starlette import ServerSentEvent, EventSourceResponse
#
# from common.logging.logger import LOGGER
# from service.generate_adv import AdvertisementGenerator
# from service.review_adv import ReviewAdvertisement
#
#
# class RequestParam(BaseModel):
#     query: str = ''
#     session_id: str = ''
#     service_id: str = ''
#     user_id: str = ''
#     channel: str = ''
#     ad_text: str = ''
#     generate_image: bool = False
#
#
# def set_request_params(request: RequestParam) -> Dict[str, Any]:
#     """
#     RequestParam 객체에서 필요한 파라미터를 추출하여 딕셔너리 형태로 반환합니다.
#     """
#     return {
#         "query": request.query,
#         "session_id": request.session_id,
#         "service_id": request.service_id,
#         "user_id": request.user_id,
#         "channel": request.channel,
#         "ad_text": request.ad_text,
#         "generate_image": request.generate_image
#     }
#
#
# router = APIRouter(
#     prefix="/apis",
#     tags=["agent_adcensor"],
#     responses={404: {"description": "Not found"}},
# )
#
#
# @router.get("/")
# async def root():
#     return JSONResponse(status_code=200, content={"message": "Advertisement Censor For Shinhan Card"},
#                         media_type="application/json")
#
#
# @router.post("/generate_adv")
# async def generate_adv(request: RequestParam):
#     param = set_request_params(request)
#     generator = AdvertisementGenerator(
#         model_name="gpt-4o",
#         template_path=Path(__file__).resolve().parent.parent / "resources/prompts/ux_writing_guide.yaml",
#         # template_path=Path(__file__).resolve().parent.parent / "resources/prompts/ReAct_generate_adv.yaml",
#         query=param["query"],
#         session_id=param["session_id"],
#         service_id=param["service_id"],
#         user_id=param["user_id"],
#         channel=param["channel"]
#     )
#     content = await generator.generate()
#     img_url = ''  # await generator.generate_image(content["content"])
#     try:
#         json_response = JSONResponse(status_code=200, content={"response": content, "img_url": img_url},
#                                      media_type="application/json")
#     except Exception as e:
#         LOGGER.error(str(e))
#         return JSONResponse(status_code=500, content={"error": f"Internal server error: {str(e)}"})
#     return json_response
#
#
# @router.post("/review_adv")
# async def review_adv(request: RequestParam):
#     param = set_request_params(request)
#     generator = ReviewAdvertisement(
#         model_name="gpt-4o",
#         template_path=Path(__file__).resolve().parent.parent / "resources/prompts/review_advertisement.yaml",
#         # template_path=Path(__file__).resolve().parent.parent / "resources/prompts/ReAct_review_adv.yaml",
#         query=param["query"],
#         session_id=param["session_id"],
#         service_id=param["service_id"],
#         user_id=param["user_id"],
#         channel=param["channel"],
#         ad_text=param["ad_text"]
#     )
#     content = await generator.generate()
#     try:
#         json_response = JSONResponse(status_code=200, content=content, media_type="application/json")
#     except Exception as e:
#         LOGGER.error(str(e))
#         return JSONResponse(status_code=500, content={"error": f"Internal server error: {str(e)}"})
#     return json_response
#
#
# @router.post("/generate_adv_stream")
# async def generate_adv_stream(request: RequestParam):
#     param = set_request_params(request)
#     generator = AdvertisementGenerator(
#         model_name="gpt-4o",
#         template_path=Path(__file__).resolve().parent.parent / "resources/prompts/ux_writing_guide.yaml",
#         # template_path=Path(__file__).resolve().parent.parent / "resources/prompts/ReAct_generate_adv.yaml",
#         query=param["query"],
#         session_id=param["session_id"],
#         service_id=param["service_id"],
#         user_id=param["user_id"],
#         channel=param["channel"]
#     )
#     img_url = ''  # await generator.generate_image(content["content"])
#
#     # Generator를 통해 SSE 이벤트 전송
#     async def event_publisher():
#         try:
#             content = ''
#             async for chunk in generator.generate_stream():  # 스트림 데이터를 chunk 단위로 생성
#                 # ServerSentEvent 객체를 사용하여 이벤트 데이터 전송
#                 event = ServerSentEvent(data=json.dumps(chunk))
#                 content += chunk
#                 yield event.encode()
#                 # await asyncio.sleep(0.1)  # 전송 속도 조절 (필요 시 조절 가능)
#             print(f"param : {param['generate_image']}")
#             print(f"content : {content}")
#             if param["generate_image"]:
#                 url = await generator.generate_image(content)
#                 img_event = ServerSentEvent(data=json.dumps(url))
#                 yield img_event.encode()
#         except Exception as e:
#             LOGGER.error(f"Stream error: {str(e)}")
#             yield ServerSentEvent(data=json.dumps({"error": str(e)}), event="error").encode()
#
#     return EventSourceResponse(event_publisher(), media_type="text/event-stream", ping=60)
#
#
# @router.post("/review_adv_stream")
# async def review_adv_stream(request: RequestParam):
#     param = set_request_params(request)
#     generator = ReviewAdvertisement(
#         model_name="gpt-4o",
#         template_path=Path(__file__).resolve().parent.parent / "resources/prompts/review_advertisement2.yaml",
#         # template_path=Path(__file__).resolve().parent.parent / "resources/prompts/ReAct_review_adv.yaml",
#         query=param["query"],
#         session_id=param["session_id"],
#         service_id=param["service_id"],
#         user_id=param["user_id"],
#         channel=param["channel"],
#         ad_text=param["ad_text"]
#     )
#
#     # Generator를 통해 SSE 이벤트 전송
#     async def event_publisher():
#         try:
#             async for chunk in generator.generate_stream():  # 스트림 데이터를 chunk 단위로 생성
#                 # ServerSentEvent 객체를 사용하여 이벤트 데이터 전송
#                 event = ServerSentEvent(data=json.dumps(chunk))
#                 yield event.encode()
#                 # await asyncio.sleep(0.1)  # 전송 속도 조절 (필요 시 조절 가능)
#         except Exception as e:
#             LOGGER.error(f"Stream error: {str(e)}")
#             yield ServerSentEvent(data=json.dumps({"error": str(e)}), event="error").encode()
#
#     return EventSourceResponse(event_publisher(), media_type="text/event-stream", ping=60)
