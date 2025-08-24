import os
import sys
# print(sys.path)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
# print(sys.path)

from utils.llm import spark_x1_response

# def answer(markdown: str, query: str,stream = False) -> str:
#     """
#     接收markdown文本和用户query，构造prompt并调用大模型API，返回回答
#     """
#     # TODO: 实现prompt构建与API请求

#     user_prompt="""你是一个数据分析专家，我将会给你一个表格的文本表示，请你根据表格文本的内容，回答\
# 我的问题。

# ##表格文本的内容如下：
# {table_text}

# ##我的问题是:{query}
# """
#     user_prompt = user_prompt.format(table_text=markdown,query=query)

#     if not stream:
#         think,answer = spark_x1_response(user_prompt,stream=stream)
#         return think,answer
#     # 流式输出
#     else:
#         think=""
#         answer=""
#         for t,a in spark_x1_response(user_prompt,stream=stream):
#             if t:
#                 think += t
#                 print(f"{t}", end="", flush=True)
#             if a:
#                 answer += a
#                 print(f"{a}", end="", flush=True)
#         return think,answer

def answer(markdown: str, query: str,stream = False) -> str:
    """
    接收markdown文本和用户query，构造prompt并调用大模型API，返回回答
    """
    # TODO: 实现prompt构建与API请求

    user_prompt="""你是一个数据分析专家，我将会给你一个表格的文本表示，请你根据表格文本的内容，回答\
我的问题。

##表格文本的内容如下：
{table_text}

##我的问题是:{query}
"""
    user_prompt = user_prompt.format(table_text=markdown,query=query)

    if not stream:
        think,answer = spark_x1_response(user_prompt,stream=stream)
        return think,answer
    # 流式输出
    else:
        def generate_stream(): # 返回生成器对象
            """生成器函数，产生SSE格式的数据块"""
            try:
                # all_think = ""  # 用于累积思考内容
                # all_answer = ""  # 用于累积回答内容
                
                for t, a in spark_x1_response(user_prompt,stream=stream):
                    # # 累积完整内容
                    # if t :
                    #     all_think += t
                    # if a:
                    #     all_answer += a
                                 
                    # 当前区块数据
                    chunk = {
                        "type": "delta", # 增量包
                        "think": t if t else None,
                        "answer": a if a else None,
                        "completed": False,
                    }
                    
                    # SSE格式: data: {json}\n\n
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                
                # 最终完成包
                completion = {
                    "type": "completion",
                    "think": "",
                    "answer": "",
                    "completed": True,
                }
                yield f"data: {json.dumps(completion, ensure_ascii=False)}\n\n"
                
                # 可选：发送结束信号
                # yield "event: end\ndata: \n\n"
            
            except Exception as e:
                # 错误处理
                error_data = {
                    "type": "error",
                    "message": str(e),
                    "error": True
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        # 返回生成器对象
        return generate_stream()

if __name__ == '__main__':

    result = answer(markdown="| 姓名 | 分数 |\n|------|------|\n| 张三 | 95   |", query="谁得了最高分")
    print(result)