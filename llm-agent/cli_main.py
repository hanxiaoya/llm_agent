# coding=utf-8

import time
from tools import tools_map
from prompt_cn import gen_prompt, user_prompt
from model_provider import ModelProvider
from dotenv import load_dotenv

load_dotenv()

# agent入口

"""
todo:
    1. 环境变量的设置
    2. 工具的引入
    3. prompt模板
    4. 模型的初始化
"""

mp = ModelProvider()


def parse_thoughts(response):
    """
        response:
        {
            "action": {
                "name": "action name",
                "args": {
                    "args name": "args value"
                }
            },
            "thoughts":
            {
                "text": "thought",
                "plan": "plan",
                "criticism": "criticism",
                "speak": "当前步骤，返回给用户的总结",
                "reasoning": ""
            }
        }
    """
    try:
        thoughts = response.get("thoughts")
        observation = response.get("observation")
        plan = thoughts.get("plan")
        reasoning = thoughts.get("reasoning")
        criticism = thoughts.get("criticism")
        prompt = f"plan: {plan}\nreasoning:{reasoning}\ncriticism: {criticism}\nobservation:{observation}"
        print("thoughts:", prompt)
        return prompt
    except Exception as err:
        print("parse thoughts err: {}".format(err))
        return "".format(err)


def agent_execute(query, max_request_time=10):
    cur_request_time = 0
    chat_history = []
    agent_scratch = ''

    while cur_request_time < max_request_time:
        cur_request_time += 1

        """
        如果返回结果达到预期，则直接返回
        """
        """
        prompt包含的功能:
            1. 任务描述
            2. 工具描述
            3. 用户的输入user_msg
            4. assistant_msg
            5. 限制
            6. 给出更好实践的描述
            
        """
        prompt = gen_prompt(query, agent_scratch)
        start_time = time.time()
        print("*************** {}. 开始调用大模型llm.......".format(cur_request_time), flush=True)
        # call llm
        """
        sys_prompt: 
        user_msg, assistant, history
        """
        if cur_request_time < 3:
            print("prompt:", prompt)
        response = mp.chat(prompt, chat_history)
        end_time = time.time()
        print("*************** {}. 调用大模型结束，耗时:{}.......".format(cur_request_time, end_time - start_time), flush=True)

        if not response or not isinstance(response, dict):
            print("调用大模型错误，即将重试....", response)
            continue

        """
        response:
        {
            "action": {
                "name": "action name",
                "args": {
                    "args name": "args value"
                }
            },
            "thoughts":
            {
                "text": "thought",
                "plan": "plan",
                "criticism": "criticism",
                "speak": "当前步骤，返回给用户的总结",
                "reasoning": ""
            }
        }
        """

        action_info = response.get("action")
        action_name = action_info.get('name')
        action_args = action_info.get('args')
        print("当前action name: ", action_name, action_args)

        if action_name == "finish":
            final_answer = action_args.get("answer")
            print("final_answer:", final_answer)
            break

        observation = response.get("observation")
        try:
            """
                action_name到函数的映射： map -> {action_name: func}
            """
            # tools_map的实现
            func = tools_map.get(action_name)
            call_func_result = func(**action_args)

        except Exception as err:
            print("调用工具异常:", err)
            call_func_result = "{}".format(err)
        agent_scratch = agent_scratch + "\n: observation: {}\n execute action result: {}".format(observation,
                                                                                                 call_func_result)

        assistant_msg = parse_thoughts(response)
        chat_history.append([user_prompt, assistant_msg])
    if cur_request_time == max_request_time:
        print("很遗憾，本次任务失败")
    else:
        print("恭喜你，任务完成")


def main():
    # 需求: 支持用户的多次交互
    max_request_time = 30
    while True:
        query = input("请输入您的目标:")
        if query == "exit":
            return
        agent_execute(query, max_request_time=max_request_time)


if __name__ == "__main__":
    main()
