import os
from openai import OpenAI
import openai

def spark_x1_response(user_prompt,stream=False):
    if not stream:
        return _spark_x1_response_direct(user_prompt)
    else:
        return _spark_x1_response_stream(user_prompt)
    

def _spark_x1_response_direct(user_prompt,stream=False):
    client = OpenAI(
        # x1 
        api_key="KpvsQcuLyVRUvOwrjOHx:oLXdBzlgoXDPrzBcmCeB", # 两种方式：1、http协议的APIpassword； 2、ws协议的apikey和apisecret 按照ak:sk格式拼接；
        base_url="https://spark-api-open.xf-yun.com/v2",
    )

    stream_res = stream


    output = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": user_prompt
            },

        ],

        model="x1",
        stream=stream_res,
        # user=user_id,

    )
    
    reasoning = ""
    response = ""

    if not stream_res:
        reasoning += output.choices[0].message.reasoning_content
        response += output.choices[0].message.content
        return reasoning,response

def _spark_x1_response_stream(user_prompt,stream=True):
    client = OpenAI(
        # x1 
        api_key="KpvsQcuLyVRUvOwrjOHx:oLXdBzlgoXDPrzBcmCeB", # 两种方式：1、http协议的APIpassword； 2、ws协议的apikey和apisecret 按照ak:sk格式拼接；
        base_url="https://spark-api-open.xf-yun.com/v2",
    )

    stream_res = stream


    output = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": user_prompt
            },

        ],

        model="x1",
        stream=stream_res,
        # user=user_id,

    )

    for chunk in output:
            reasoning_chunk = ""
            content_chunk = ""
            
            if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content is not None:
                reasoning_chunk = chunk.choices[0].delta.reasoning_content
            else:
                reasoning_chunk = None
            
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                content_chunk = chunk.choices[0].delta.content
            else:
                content_chunk = None
            
            # 实时产出当前片段
            yield reasoning_chunk, content_chunk

if __name__ == '__main__':

    spark_x1_response(user_prompt="请你重复我们刚才的对话",stream=True)