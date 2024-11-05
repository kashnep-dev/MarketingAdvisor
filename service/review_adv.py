import json
from pathlib import Path
from typing import Any, Dict, Iterator

import pandas as pd
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import load_prompt
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from common.logging.logger import LOGGER
from common.util.adcensor_util import get_message_history
from common.util.callback_handler import NonStreamCallbackHandler, StreamCallbackHandler
import time

class ReviewAdvertisement:

    def __init__(self, model_name: str, template_path: Path, query: str, session_id: str, service_id: str, user_id: str, channel: str, ad_text: str):
        # 공통
        self.model_name = model_name
        self.template_path = template_path
        self.query = query
        self.channel = channel
        self.memory_window_size = 10
        self.ad_text = ad_text

        # insert logs
        self.session_id = session_id
        self.service_id = service_id
        self.user_id = user_id
        self.trace_id = ''
        LOGGER.info("Start ReviewAdvertisement")

    @staticmethod
    def parse_checklist():
        df = pd.read_excel(r'C:\Users\user\Desktop\checklist_26.xlsx')
        print(df.head())
        # df["세부항목_구분"] = df.iloc[:, 0] + "_" + df.iloc[:, 1]
        # filtered_df = df[df['세부항목'].isin(['Trustworthy', 'Casual'])]
        filtered_df = df
        # checklist = filtered_df.to_string(index=False)
        checklist = filtered_df.to_markdown(index=False)
        return checklist

    def _set_chain(self) -> RunnableWithMessageHistory:
        model = ChatOpenAI(model_name=self.model_name, temperature=0)
        ad_censor_guide = load_prompt(self.template_path, encoding="utf-8").format()

        prompt_template = ChatPromptTemplate(
            [
                ("system", ad_censor_guide),
                ("system", f"다음은 광고문구입니다: <ad_text>{self.ad_text}<ad_text>"),
                ("system", f"다음은 체크리스트입니다: <checklist>{self.parse_checklist()}<checklist>"),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{query}"),
                ("assistant", "다음은 광고 심의 결과입니다:")
            ]
        )

        chain = prompt_template | model | StrOutputParser()
        chain_with_history = RunnableWithMessageHistory(
            chain,
            lambda session_id: get_message_history(self.session_id, self.memory_window_size),
            input_messages_key="query",
            history_messages_key="history",
        )
        return chain_with_history

    async def generate(self) -> Dict[str, Any]:
        chain_with_history = self._set_chain()
        callback_handler = NonStreamCallbackHandler(self.session_id, self.service_id, self.user_id, self.query)
        config = {"callbacks": [callback_handler], "configurable": {"session_id": self.session_id}}
        chain_with_history.invoke({"query": self.query}, config=config)
        result = callback_handler.result
        return result

    async def generate_stream(self):
        chain_with_history = self._set_chain()
        callback_handler = StreamCallbackHandler(self.session_id, self.service_id, self.user_id, self.query, self.model_name)
        config = {"callbacks": [callback_handler], "configurable": {"session_id": self.session_id}}
        response = chain_with_history.astream({"query": self.query}, config=config)
        async for chunk in response:
            yield chunk

def review_advertisement2(ad_text, checklist):
    pass
    # # 시간 측정 시작
    # start_time = time.time()
    #
    # # LLM 설정
    # llm_start = time.time()
    # llm = ChatOpenAI(model_name="gpt-4o", temperature=0, api_key=env.get("OPENAI_API_KEY"))
    # llm_end = time.time()
    # print(f"LLM 설정 시간: {llm_end - llm_start:.4f} 초")
    #
    # # 템플릿 로드
    # template_start = time.time()
    # base_path = Path(__file__).resolve().parent.parent
    # template_path = base_path / "resources/prompts/review_advertisement.yaml"
    # template = load_prompt(template_path, encoding="utf-8")
    # template_end = time.time()
    # print(f"템플릿 로드 시간: {template_end - template_start:.4f} 초")
    #
    # # 체크리스트 분할 및 체인 생성
    # chain_start = time.time()
    # checklist_items = split_checklist(checklist)
    # chains = {
    #     f"chain{idx}": PromptTemplate.from_template(template=template.format(ad_text=ad_text, checklist=item)) | llm
    #     for idx, item in enumerate(checklist_items)
    # }
    # chain_end = time.time()
    # print(f"체인 생성 시간: {chain_end - chain_start:.4f} 초")
    #
    # # 병렬 실행
    # parallel_start = time.time()
    # parallel_chain = RunnableParallel(runnable=chains)
    # response = parallel_chain.invoke({"query": "다음 지시에 따라 작성 해줘."})
    # # response = chains['chain0'].invoke({"query": "다음 지시에 따라 작성 해줘"})
    # parallel_end = time.time()
    # print(f"병렬 실행 시간: {parallel_end - parallel_start:.4f} 초")
    #
    # # 응답 처리 및 토큰 합산
    # response_start = time.time()
    # response_list = [
    #     {
    #         "content": json.loads(response['runnable'][key].content),
    #         "model_name": response['runnable'][key].response_metadata['model_name'],
    #         "input_token": response['runnable'][key].usage_metadata['input_tokens'],
    #         "output_token": response['runnable'][key].usage_metadata['output_tokens'],
    #         "input_cost": get_openai_token_cost_for_model(response['runnable'][key].response_metadata['model_name'],
    #                                                       response['runnable'][key].usage_metadata['input_tokens'],
    #                                                       False),
    #         "output_cost": get_openai_token_cost_for_model(response['runnable'][key].response_metadata['model_name'],
    #                                                        response['runnable'][key].usage_metadata['output_tokens'],
    #                                                        True),
    #         # "content": json.loads(response.content),
    #         # "model_name": response.response_metadata['model_name'],
    #         # "input_token": response.usage_metadata['input_tokens'],
    #         # "output_token": response.usage_metadata['output_tokens']
    #     }
    #     for key in chains.keys()
    # ]
    # response_end = time.time()
    # print(f"응답 처리 시간: {response_end - response_start:.4f} 초")
    #
    # # 토큰 합산
    # token_sum_start = time.time()
    # input_token_sum = sum(item['input_token'] for item in response_list)
    # output_token_sum = sum(item['output_token'] for item in response_list)
    # input_cost_sum = sum(item['input_cost'] for item in response_list)
    # output_cost_sum = sum(item['output_cost'] for item in response_list)
    # token_sum_end = time.time()
    # print(f"토큰 합산 시간: {token_sum_end - token_sum_start:.4f} 초")
    #
    # end_time = time.time()
    # print(f"총 실행 시간: {end_time - start_time:.4f} 초")
    #
    # # return response
    # return {
    #     'response_list': response_list,
    #     'input_token_sum': input_token_sum,
    #     'output_token_sum': output_token_sum,
    #     'input_cost_sum': input_cost_sum,
    #     'output_cost_sum': output_cost_sum
    # }
