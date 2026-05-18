import openai
from openai import OpenAI
client = OpenAI()

import json
import time
import os 

client_qwen_vllm = OpenAI(
    # If environment variables are not configured, replace the following line with: api_key="sk-xxx",
    api_key="EMPTY", 
    base_url="http://localhost:8000/v1",
)
def ask_vllm(messages, gpt_model="Qwen/Qwen3-8B", ifjson=False, temp=0.6, try_times=0,enable_thinking=True):
    try:
        try_times += 1

        if ifjson:
            completion = client_qwen_vllm.chat.completions.create(
                model=gpt_model,
                response_format={"type": "json_object"},
                messages=messages,
                temperature=temp,
                top_p=0.95,
                max_tokens=4096,
                extra_body={"chat_template_kwargs": {"enable_thinking": enable_thinking}},
    
            )
            content = completion.choices[0].message.content
            content = json.loads(content)
            if content is not None:
                # print("\n***ASK QWEN VLLM***\n")
                # print(content)
                # print("\n****************\n")
                return content
        else:
            completion = client_qwen_vllm.chat.completions.create(
                model=gpt_model,
                messages=messages,
                temperature=temp,
                top_p=0.95,
                max_tokens=4096,
                extra_body={"chat_template_kwargs": {"enable_thinking": enable_thinking}},
            )
            content = completion.choices[0].message.content
            if "I'm sorry" in content or "I’m sorry" in content:
                if try_times > 3:
                    return content
                else:
                    if len(messages) == 1:
                        messages.insert(0, {"role": "system", "content": "You are a helpful assistant. You can help me by answering my questions. You can also ask me questions."})
                    return ask_vllm(messages, gpt_model, ifjson, temp, try_times,enable_thinking)
            if content is not None:
                return content

    except openai.RateLimitError as e:
        # 从错误信息中提取等待时间
        wait_time = 5  # 默认等待时间
        if 'Please try again in' in str(e):
            try:
                wait_time = float(str(e).split('Please try again in')[1].split('s')[0].strip())
            except ValueError:
                pass
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
        time.sleep(wait_time)
        return ask_vllm(messages, gpt_model, ifjson, temp, try_times)  # 递归调用以重试请求

    except Exception as e:
        print(f"Error in ask_qwen: {e}")
        if try_times > 2:
            print("Error in processing the request", messages)
            return None
        return ask_vllm(messages, gpt_model, ifjson, temp, try_times)  # 递归调用以重试请求