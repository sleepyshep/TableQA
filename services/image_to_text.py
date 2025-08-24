from fastapi import UploadFile
from utils.qwen import qwen_api
from utils.latex2img import latex_to_image
# from utils.latex2excel import latex_table_to_excel
import os

UPLOAD_DIR = "/home/yangxuzheng/Workplace/fastapi/images/"
async def run_model(file: UploadFile) -> str:
    """
    接收图像文件, 调用本地模型, 返回LaTeX
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    latex = qwen_api(file_path)
    
    img = latex_to_image(latex)

    # excel = latex_table_to_excel(latex)
    # excel = None
    return latex, img