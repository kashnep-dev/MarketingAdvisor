"""
@ FileName : generate_adv.py
@ Description : 광고 문구와 시안 이미지를 생성한다.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterator

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import load_prompt
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from openai import OpenAI

from common.logging.logger import LOGGER
from common.util.adcensor_util import get_message_history
from common.util.callback_handler import NonStreamCallbackHandler, StreamCallbackHandler
from common.util.environment import env
import pandas as pd


class AdvertisementGenerator:

    def __init__(self, model_name: str, template_path: Path, query: str, session_id: str, service_id: str, user_id: str, channel: str):
        # 공통
        self.model_name = model_name
        self.template_path = template_path
        self.query = query
        self.channel = channel
        self.memory_window_size = 10

        # insert logs
        self.session_id = session_id
        self.service_id = service_id
        self.user_id = user_id
        self.trace_id = ''
        LOGGER.info("Start AdvertisementGenerator")

    @staticmethod
    def parse_checklist():
        df = pd.read_excel(os.path.join(os.environ["WORK_DIR"], "resources", "checklist", "checklist_26.xlsx"))
        checklist = df.to_markdown(index=False)
        return checklist

    def _set_chain(self) -> RunnableWithMessageHistory:
        model = ChatOpenAI(model_name=self.model_name, temperature=0)
        ux_writing_guide = load_prompt(self.template_path, encoding="utf-8").format()
        prompt_template = ChatPromptTemplate(
            [
                ("system", ux_writing_guide),
                ("system", f"다음은 체크리스트입니다: <ad_text>{self.parse_checklist()}<ad_text>"),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{query}")
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

    def generate_stream(self):
        chain_with_history = self._set_chain()
        callback_handler = StreamCallbackHandler(self.session_id, self.service_id, self.user_id, self.query, self.model_name)
        config = {"callbacks": [callback_handler], "configurable": {"session_id": self.session_id}}
        response = chain_with_history.stream({"query": self.query}, config=config)
        for chunk in response:
            yield chunk

    @staticmethod
    def generate_image(prompt):
        client = OpenAI(api_key=env.get("OPENAI_API_KEY"))
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                quality="hd",
                size="1024x1024"
            )

            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt
            # return {'image_url': image_url, 'revised_prompt': revised_prompt}
            print(image_url)
            return image_url

        except Exception as e:
            import ast

            error_string = e.args[0]
            error_dict = ast.literal_eval(error_string[18:])

            # error의 code와 message 추출
            error_code = error_dict['error']['code']
            error_message = error_dict['error']['message']

            print(f"Error code: {error_code}")
            print(f"Error message: {error_message}")
            print(f"An error occurred: {e}")
            return {
                "code": error_code,
                "message": error_message
            }
