"""
Unified LLM Interface Module

统一的LLM调用接口，支持GPT-4o和VLLM
从build_corpus_1207.py lines 706-800提取
"""

import json
import time
from typing import Dict, Optional, Any
from openai import OpenAI
import openai

from .vllm_client import ask_vllm

# Initialize OpenAI client
client = OpenAI()


def ask_gpt(system_prompt: str, user_prompt: str, temp: float = 0.1) -> Dict:
    """
    GPT-4o接口

    Args:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
        temp: 温度参数

    Returns:
        Dict: LLM返回的JSON对象

    Note: From build_corpus_1207.py lines 755-794
    """
    try_times = 0
    try:
        try_times += 1

        completion = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temp,
        )
        content = completion.choices[0].message.content
        content = json.loads(content)
        if content is not None:
            return content

    except openai.RateLimitError as e:
        # 从错误信息中提取等待时间
        wait_time = 30  # 默认等待时间
        if 'Please try again in' in str(e):
            try:
                wait_time = float(str(e).split('Please try again in')[1].split('s')[0].strip())
            except ValueError:
                pass
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
        time.sleep(wait_time)
        return ask_gpt(system_prompt, user_prompt, temp)  # 递归调用以重试请求

    except Exception as e:
        print(f"Error: {e}")
        if try_times > 3:
            print("Increase the temperature")
            temp += 0.1
            return ask_gpt(system_prompt, user_prompt, temp)
        print("Error RETRY")
        return ask_gpt(system_prompt, user_prompt, temp)


def ask_llama(system_prompt: str, user_prompt: str, pipe: Any, temp: float = 0.1) -> Dict:
    """
    Llama/VLLM接口

    Args:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
        pipe: Pipeline对象（当前实现中为字符串"llama"）
        temp: 温度参数

    Returns:
        Dict: LLM返回的JSON对象

    Note: From build_corpus_1207.py lines 706-753
    """
    try_times = 0
    system_prompt_toadd = """First, give some analysis, and then return JSON(refer to the above example, you need to follow the instruction to fill the ...) between OUTPUT_START and OUTPUT_END,make sure the json can be correctly loaded."""

    try:
        try_times += 1
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        content_json = ask_vllm(messages, ifjson=True)

        if content_json is not None:
            return content_json
        else:
            return ask_llama(system_prompt, user_prompt, pipe, temp)

    except Exception as e:
        # 如果VLLM失败，尝试用GPT修复JSON
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "Fix this json,make it can be loaded correctly"},
                    {"role": "user", "content": str(content_json)},
                ],
                temperature=temp,
            )
            content_json = completion.choices[0].message.content
            content_json = json.loads(content_json)
            if content_json is not None:
                print("\n Fixed")
                return content_json
        except:
            pass

        print(f"\n Error: {e}")
        if try_times > 3:
            print("Increase the temperature")
            temp += 0.1
            return ask_llama(system_prompt, user_prompt, pipe, temp)
        print("Error RETRY")
        return ask_llama(system_prompt, user_prompt, pipe, temp)


def ask_llm(system_prompt: str, user_prompt: str, pipe: Optional[Any] = None, temp: float = 0.1) -> Dict:
    """
    统一的LLM调用接口

    Args:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
        pipe: Pipeline对象，如果为None则使用GPT，否则使用Llama/VLLM
        temp: 温度参数

    Returns:
        Dict: LLM返回的JSON对象

    Note: From build_corpus_1207.py lines 796-800

    Example:
        >>> # 使用GPT
        >>> result = ask_llm(system_prompt, user_prompt)
        >>>
        >>> # 使用VLLM
        >>> result = ask_llm(system_prompt, user_prompt, pipe="llama")
    """
    if pipe is not None:
        return ask_llama(system_prompt, user_prompt, pipe, temp)
    else:
        return ask_gpt(system_prompt, user_prompt, temp)
