import os
import pickle
import time
import uuid
from os import path
from typing import Any, Dict, List, Optional, Sequence, Union
from uuid import UUID

from langchain_core.agents import AgentFinish, AgentAction
from langchain_core.callbacks.base import BaseCallbackHandler, AsyncCallbackHandler
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult, GenerationChunk, ChatGenerationChunk
from tenacity import RetryCallState

# from common.db import adcensor_dao as dao
# from common.db.db_connection import transactional
# from common.db.schemas.tb_generation import TbGenerationLog
# from common.db.schemas.tb_session import TbSessionLog
# from common.db.schemas.tb_trace import TbTraceLog
from common.logging.logger import LOGGER
# from common.model import TbSession, TbTrace, TbGeneration
from common.util.adcensor_util import get_openai_token_cost_for_model, get_token_size


class NonStreamCallbackHandler(BaseCallbackHandler):
    def __init__(self, session_id: str, service_id: str, user_id: str, query: str) -> None:
        self.session_id = session_id
        self.service_id = service_id
        self.user_id = user_id
        self.start_time = self.end_time = self.elapsed_time = time.time()
        self.generation_id = ''
        self.generation_text = ''
        self.usage_model_name = ''
        self.usage_token_count = self.usage_cost = 0
        self.generation_order = 0
        self.user_expose_step = False

        self.trace_id = service_id
        self.trace_order = 0
        self.prompt_id = ''
        self.input_time = time.time()
        self.user_input_yn = False

        self.query = query
        self.result = {}
        super().__init__()

    def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        self.start_time = time.time()
        LOGGER.debug("""Run when LLM starts running.""")

    def on_chat_model_start(
            self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], **kwargs: Any
    ) -> Any:
        LOGGER.debug("""Run when Chat Model starts running.""")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        # 토큰 정보 추출
        input_token = response.generations[0][0].message.response_metadata["token_usage"]["prompt_tokens"]
        output_token = response.generations[0][0].message.response_metadata["token_usage"]["completion_tokens"]
        self.usage_token_count = input_token + output_token

        # 기타 정보 추출
        self.generation_text = response.generations[0][0].text
        self.usage_model_name = response.generations[0][0].message.response_metadata["model_name"]
        self.generation_id = response.generations[0][0].message.id
        self.end_time = time.time()
        input_cost = get_openai_token_cost_for_model(self.usage_model_name, input_token, False)
        output_cost = get_openai_token_cost_for_model(self.usage_model_name, output_token, True)
        self.usage_cost = input_cost + output_cost

        # 총 실행 시간 로깅
        self.end_time = time.time()
        self.elapsed_time = int(self.end_time - self.start_time)
        LOGGER.debug(f"총 실행 시간: {self.elapsed_time} 초")

        self.result = {
            "content": self.generation_text,
            "model_name": self.usage_model_name,
            "input_token": input_token,
            "output_token": output_token,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "elapsed_time": self.elapsed_time
        }

        # self.save_session_log()
        # self.save_generation_log()
        # self.save_trace_log()

        # self.send_session_log()
        # self.send_generation_log()
        # self.send_trace_log()

        LOGGER.debug("""Run when LLM ends running.""")

    def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        LOGGER.debug("""Run on new LLM token. Only available when streaming is enabled.""")

    def on_chain_start(
            self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> Any:
        LOGGER.debug("""Run when chain starts running.""")

    def save_log_to_pickle(self, data, filename):
        """ 데이터를 pickle 파일로 저장하는 함수 """
        with open(filename, 'wb') as f:
            pickle.dump(data, f)

    # def save_session_log(self):
    #     tb_session = TbSession(
    #         SESSION_ID=uuid.uuid4().hex[:20],
    #         # SESSION_ID=self.session_id,
    #         SERVICE_ID=self.service_id,
    #         USER_ID=self.user_id,
    #         CREATE_DT=self.start_time,
    #         END_DT=self.end_time,
    #         DURATION_TIME=self.elapsed_time,
    #         TRACE_COUNT=0,
    #         USAGE_COST=self.usage_cost,
    #         USAGE_TOKEN_COUNT=self.usage_token_count
    #     )
    #     work_dir = os.environ['WORK_DIR']
    #     filename = f"{str(time.time_ns())}.pkl"
    #     session_log_path = path.join(work_dir, "resources", "logs", "session", filename)
    #     self.save_log_to_pickle(tb_session, session_log_path)
    #
    # def save_generation_log(self):
    #     tb_generation = TbGeneration(
    #         GENERATION_ID=self.generation_id,
    #         GENERATION_ORDER=self.generation_order,
    #         GENERATION_TEXT=self.generation_text,
    #         RESPONSE_START_TIME_STREAM=self.start_time,
    #         RESPONSE_END_TIME=self.end_time,
    #         RESPONSE_DURATION_TIME=self.elapsed_time,
    #         RESPONSE_START_TIME=self.start_time,
    #         USER_EXPOSE_STEP=self.user_expose_step,
    #         USER_EXPOSE_TEXT='',
    #         USAGE_COST=self.usage_cost,
    #         USAGE_TOKEN_COUNT=self.usage_token_count,
    #         USAGE_MODEL_NAME=self.usage_model_name
    #     )
    #     work_dir = os.environ['WORK_DIR']
    #     filename = f"{str(time.time_ns())}.pkl"
    #     generation_log_path = path.join(work_dir, "resources", "logs", "generation", filename)
    #     self.save_log_to_pickle(tb_generation, generation_log_path)
    #
    # def save_trace_log(self):
    #     tb_trace = TbTrace(
    #         # TRACE_ID=self.session_id,
    #         TRACE_ID=uuid.uuid4().hex[:20],
    #         TRACE_CONTENT=self.generation_text,
    #         TRACE_ORDER=self.trace_order,
    #         SESSION_ID=self.session_id,
    #         PROMPT_ID=self.prompt_id,
    #         INPUT_TIME=self.input_time,
    #         USER_INPUT_YN=self.user_input_yn,
    #         USER_INPUT_TEXT=self.query,
    #         USAGE_COST=self.usage_cost,
    #         USAGE_TOKEN_COUNT=self.usage_token_count
    #     )
    #     work_dir = os.environ['WORK_DIR']
    #     filename = f"{str(time.time_ns())}.pkl"
    #     trace_log_path = path.join(work_dir, "resources", "logs", "trace", filename)
    #     self.save_log_to_pickle(tb_trace, trace_log_path)
    #
    # @transactional
    # def send_session_log(self):
    #     """
    #     세션 로그를 DB에 저장 한다.
    #     """
    #     tb_session = TbSession(
    #         # SESSION_ID=self.session_id,
    #         SESSION_ID=uuid.uuid4().hex[:20],
    #         SERVICE_ID=self.service_id,
    #         USER_ID=self.user_id,
    #         CREATE_DT=self.start_time,
    #         END_DT=self.end_time,
    #         DURATION_TIME=self.elapsed_time,
    #         TRACE_COUNT=0,
    #         USAGE_COST=self.usage_cost,
    #         USAGE_TOKEN_COUNT=self.usage_token_count
    #     )
    #     dao.insert_session_log(TbSessionLog(tb_session))
    #
    # @transactional
    # def send_generation_log(self):
    #     """
    #     생성 로그를 DB에 저장 한다.
    #     """
    #     tb_generation = TbGeneration(
    #         GENERATION_ID=self.generation_id,
    #         GENERATION_ORDER=self.generation_order,
    #         GENERATION_TEXT=self.generation_text,
    #         RESPONSE_START_TIME_STREAM=self.start_time,
    #         RESPONSE_END_TIME=self.end_time,
    #         RESPONSE_DURATION_TIME=self.elapsed_time,
    #         RESPONSE_START_TIME=self.start_time,
    #         USER_EXPOSE_STEP=self.user_expose_step,
    #         USER_EXPOSE_TEXT='',
    #         USAGE_COST=self.usage_cost,
    #         USAGE_TOKEN_COUNT=self.usage_token_count,
    #         USAGE_MODEL_NAME=self.usage_model_name
    #     )
    #     dao.insert_generation_log(TbGenerationLog(tb_generation))
    #
    # @transactional
    # def send_trace_log(self):
    #     """
    #     이력 로그를 DB에 저장 한다.
    #     """
    #     tb_trace = TbTrace(
    #         # TRACE_ID=self.trace_id,
    #         TRACE_ID=uuid.uuid4().hex[:20],
    #         TRACE_CONTENT=self.generation_text,
    #         TRACE_ORDER=self.trace_order,
    #         SESSION_ID=self.session_id,
    #         PROMPT_ID=self.prompt_id,
    #         INPUT_TIME=self.input_time,
    #         USER_INPUT_YN=self.user_input_yn,
    #         USER_INPUT_TEXT=self.query,
    #         USAGE_COST=self.usage_cost,
    #         USAGE_TOKEN_COUNT=self.usage_token_count
    #     )
    #     dao.insert_generation_log(TbTraceLog(tb_trace))


class StreamCallbackHandler(AsyncCallbackHandler):
    def __init__(self, session_id: str, service_id: str, user_id: str, query: str, model_name: str) -> None:
        self.session_id = session_id
        self.service_id = service_id
        self.user_id = user_id
        self.start_time = self.end_time = self.elapsed_time = time.time()
        self.generation_id = ''
        self.generation_text = ''
        self.usage_model_name = model_name
        self.usage_token_count = self.input_token_count = self.output_token_count = 0
        self.usage_cost = self.input_cost = self.output_cost = 0
        self.generation_order = 0
        self.user_expose_step = False

        self.trace_id = service_id
        self.trace_order = 0
        self.prompt_id = ''
        self.input_time = time.time()
        self.user_input_yn = False

        self.query = query
        self.result = {}
        super().__init__()

    async def on_chat_model_start(
            self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], **kwargs: Any
    ) -> Any:
        for msg in messages[0]:
            self.input_token_count += get_token_size(msg.content, self.usage_model_name)
        self.input_cost = get_openai_token_cost_for_model(self.usage_model_name, self.input_token_count, False)
        LOGGER.debug("input_token_count : " + str(self.input_token_count))
        LOGGER.debug("input_count : " + str(self.input_cost))
        LOGGER.debug("""Run when Chat Model starts running.""")

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        LOGGER.debug("""Run when LLM ends running.""")
        print("""Run when LLM ends running.""")
        self.generation_id = response.generations[0][0].message.id
        self.generation_text = response.generations[0][0].text
        self.usage_model_name = response.generations[0][0].message.response_metadata["model_name"]
        self.output_token_count = get_token_size(self.generation_text, self.usage_model_name)
        self.output_cost = get_openai_token_cost_for_model(self.usage_model_name, self.output_token_count)
        self.usage_token_count = self.input_token_count + self.output_token_count
        self.usage_cost = self.input_cost + self.output_cost

        LOGGER.debug("generation_text : " + self.generation_text)
        LOGGER.debug("output_token_count : " + str(self.output_token_count))
        LOGGER.debug("output_cost : " + str(self.output_cost))
        LOGGER.debug("usage_token_count : " + str(self.usage_token_count))
        LOGGER.debug("usage_cost : " + str(self.usage_cost))

        # 총 실행 시간 로깅
        self.end_time = time.time()
        self.elapsed_time = int(self.end_time - self.start_time)
        LOGGER.debug(f"총 실행 시간: {self.elapsed_time} 초")
        #
        # self.send_session_log()
        # self.send_generation_log()
        # self.send_trace_log()

    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], *, run_id: UUID,
                           parent_run_id: Optional[UUID] = None, tags: Optional[List[str]] = None,
                           metadata: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        return await super().on_llm_start(serialized, prompts, run_id=run_id, parent_run_id=parent_run_id, tags=tags,
                                          metadata=metadata, **kwargs)

    async def on_llm_new_token(self, token: str, *, chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
                               run_id: UUID, parent_run_id: Optional[UUID] = None, tags: Optional[List[str]] = None,
                               **kwargs: Any) -> None:
        return await super().on_llm_new_token(token, chunk=chunk, run_id=run_id, parent_run_id=parent_run_id, tags=tags,
                                              **kwargs)

    async def on_llm_error(self, error: BaseException, *, run_id: UUID, parent_run_id: Optional[UUID] = None,
                           tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        return await super().on_llm_error(error, run_id=run_id, parent_run_id=parent_run_id, tags=tags, **kwargs)

    async def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], *, run_id: UUID,
                             parent_run_id: Optional[UUID] = None, tags: Optional[List[str]] = None,
                             metadata: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        return await super().on_chain_start(serialized, inputs, run_id=run_id, parent_run_id=parent_run_id, tags=tags,
                                            metadata=metadata, **kwargs)

    async def on_chain_end(self, outputs: Dict[str, Any], *, run_id: UUID, parent_run_id: Optional[UUID] = None,
                           tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        return await super().on_chain_end(outputs, run_id=run_id, parent_run_id=parent_run_id, tags=tags, **kwargs)

    async def on_chain_error(self, error: BaseException, *, run_id: UUID, parent_run_id: Optional[UUID] = None,
                             tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        return await super().on_chain_error(error, run_id=run_id, parent_run_id=parent_run_id, tags=tags, **kwargs)

    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, *, run_id: UUID,
                            parent_run_id: Optional[UUID] = None, tags: Optional[List[str]] = None,
                            metadata: Optional[Dict[str, Any]] = None, inputs: Optional[Dict[str, Any]] = None,
                            **kwargs: Any) -> None:
        return await super().on_tool_start(serialized, input_str, run_id=run_id, parent_run_id=parent_run_id, tags=tags,
                                           metadata=metadata, inputs=inputs, **kwargs)

    async def on_tool_end(self, output: Any, *, run_id: UUID, parent_run_id: Optional[UUID] = None,
                          tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        return await super().on_tool_end(output, run_id=run_id, parent_run_id=parent_run_id, tags=tags, **kwargs)

    async def on_tool_error(self, error: BaseException, *, run_id: UUID, parent_run_id: Optional[UUID] = None,
                            tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        return await super().on_tool_error(error, run_id=run_id, parent_run_id=parent_run_id, tags=tags, **kwargs)

    async def on_text(self, text: str, *, run_id: UUID, parent_run_id: Optional[UUID] = None,
                      tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        return await super().on_text(text, run_id=run_id, parent_run_id=parent_run_id, tags=tags, **kwargs)

    async def on_retry(self, retry_state: RetryCallState, *, run_id: UUID, parent_run_id: Optional[UUID] = None,
                       **kwargs: Any) -> Any:
        return await super().on_retry(retry_state, run_id=run_id, parent_run_id=parent_run_id, **kwargs)

    async def on_agent_action(self, action: AgentAction, *, run_id: UUID, parent_run_id: Optional[UUID] = None,
                              tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        return await super().on_agent_action(action, run_id=run_id, parent_run_id=parent_run_id, tags=tags, **kwargs)

    async def on_agent_finish(self, finish: AgentFinish, *, run_id: UUID, parent_run_id: Optional[UUID] = None,
                              tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        return await super().on_agent_finish(finish, run_id=run_id, parent_run_id=parent_run_id, tags=tags, **kwargs)

    async def on_retriever_start(self, serialized: Dict[str, Any], query: str, *, run_id: UUID,
                                 parent_run_id: Optional[UUID] = None, tags: Optional[List[str]] = None,
                                 metadata: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        return await super().on_retriever_start(serialized, query, run_id=run_id, parent_run_id=parent_run_id,
                                                tags=tags, metadata=metadata, **kwargs)

    async def on_retriever_end(self, documents: Sequence[Document], *, run_id: UUID,
                               parent_run_id: Optional[UUID] = None, tags: Optional[List[str]] = None,
                               **kwargs: Any) -> None:
        return await super().on_retriever_end(documents, run_id=run_id, parent_run_id=parent_run_id, tags=tags,
                                              **kwargs)

    async def on_retriever_error(self, error: BaseException, *, run_id: UUID, parent_run_id: Optional[UUID] = None,
                                 tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        return await super().on_retriever_error(error, run_id=run_id, parent_run_id=parent_run_id, tags=tags, **kwargs)

    async def on_custom_event(self, name: str, data: Any, *, run_id: UUID, tags: Optional[List[str]] = None,
                              metadata: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        return await super().on_custom_event(name, data, run_id=run_id, tags=tags, metadata=metadata, **kwargs)

    # @transactional
    # def send_session_log(self):
    #     """
    #     세션 로그를 DB에 저장 한다.
    #     """
    #     tb_session = TbSession(
    #         # SESSION_ID=self.session_id,
    #         SESSION_ID=uuid.uuid4().hex[:20],
    #         SERVICE_ID=self.service_id,
    #         USER_ID=self.user_id,
    #         CREATE_DT=self.start_time,
    #         END_DT=self.end_time,
    #         DURATION_TIME=self.elapsed_time,
    #         TRACE_COUNT=0,
    #         USAGE_COST=self.usage_cost,
    #         USAGE_TOKEN_COUNT=self.usage_token_count
    #     )
    #     dao.insert_session_log(TbSessionLog(tb_session))
    #
    # @transactional
    # def send_generation_log(self):
    #     """
    #     생성 로그를 DB에 저장 한다.
    #     """
    #     tb_generation = TbGeneration(
    #         GENERATION_ID=self.generation_id,
    #         GENERATION_ORDER=self.generation_order,
    #         GENERATION_TEXT=self.generation_text,
    #         RESPONSE_START_TIME_STREAM=self.start_time,
    #         RESPONSE_END_TIME=self.end_time,
    #         RESPONSE_DURATION_TIME=self.elapsed_time,
    #         RESPONSE_START_TIME=self.start_time,
    #         USER_EXPOSE_STEP=self.user_expose_step,
    #         USER_EXPOSE_TEXT='',
    #         USAGE_COST=self.usage_cost,
    #         USAGE_TOKEN_COUNT=self.usage_token_count,
    #         USAGE_MODEL_NAME=self.usage_model_name
    #     )
    #     dao.insert_generation_log(TbGenerationLog(tb_generation))
    #
    # @transactional
    # def send_trace_log(self):
    #     """
    #     이력 로그를 DB에 저장 한다.
    #     """
    #     tb_trace = TbTrace(
    #         # TRACE_ID=self.trace_id,
    #         TRACE_ID=uuid.uuid4().hex[:20],
    #         TRACE_CONTENT=self.generation_text,
    #         TRACE_ORDER=self.trace_order,
    #         SESSION_ID=self.session_id,
    #         PROMPT_ID=self.prompt_id,
    #         INPUT_TIME=self.input_time,
    #         USER_INPUT_YN=self.user_input_yn,
    #         USER_INPUT_TEXT=self.query,
    #         USAGE_COST=self.usage_cost,
    #         USAGE_TOKEN_COUNT=self.usage_token_count
    #     )
    #     dao.insert_generation_log(TbTraceLog(tb_trace))
