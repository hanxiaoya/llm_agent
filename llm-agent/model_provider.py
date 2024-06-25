# coding=utf-8

import os
import json
import dashscope
from dashscope.api_entities.dashscope_response import Message
from prompt_cn import user_prompt


class ModelProvider(object):
    def __init__(self):
        self.api_key = os.environ.get("API_KEY")
        self.model_name = os.environ.get("MODEL_NAME")
        self._client = dashscope.Generation()
        print("model_name:", self.model_name)
        self.max_retry_time = 3

    def chat(self, prompt, chat_history):
        cur_retry_time = 0
        while cur_retry_time < self.max_retry_time:
            cur_retry_time += 1
            try:
                messages = [Message(role='system', content=prompt)]
                for his in chat_history:
                    messages.append(Message(role='user', content=his[0]))
                    messages.append(Message(role='assistant', content=his[1]))
                messages.append(Message(role='user', content=user_prompt))
                response = self._client.call(
                    model=self.model_name,
                    api_key=self.api_key,
                    messages=messages
                )
                """
                {
                    "status_code": 200,
                     "request_id": "c965bd27-c89c-9b5c-924d-2f1688e8041e", 
                     "code": "", 
                     "message": "", 
                     "output": {
                        "text": null, "finish_reason": null,
                         "choices": [{
                            "finish_reason": "null", "message": 
                            {"role": "assistant", "content": "当然可以，这里有一个简单又美味"}
                        }]
                    }, 
                    "usage": {
                        "input_tokens": 31, 
                        "output_tokens": 8, 
                        "total_tokens": 39, 
                        "plugins": {}
                    }
                }
                """
                print("response:", response)

                content = json.loads(response['output']['text'])
                return content
            except Exception as err:
                print("调用大模型出错：{}".format(err))
            return {}
