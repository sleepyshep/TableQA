import base64
from openai import OpenAI
# Set OpenAI's API key and API base to use vLLM's API server.
def qwen_api(image_path: str) -> str:

    openai_api_key = "EMPTY"
    openai_api_base = "http://localhost:8007/v1"
    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )
    with open(image_path, "rb") as f:
        encoded_image = base64.b64encode(f.read())
    encoded_image_text = encoded_image.decode("utf-8")
    base64_qwen = f"data:image;base64,{encoded_image_text}"
    chat_response = client.chat.completions.create(
        model="/home/lingjun/code/qwenvl/",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": base64_qwen
                        },
                    },
                    {"type": "text", "text": "<image>\nConvert this table to LaTeX."},
                ],
            },
        ],
    )
    return str(chat_response.choices[0].message.content)

if __name__ == '__main__':
    result = qwen_api(image_path="/home/yangxuzheng/Workplace/fastapi/images/simple.png")
    print(result)