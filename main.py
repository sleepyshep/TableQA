from fastapi import FastAPI
from routers import api
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Table Recognition & QA",
    description="Image → Latex → Markdown + Image → QA",
    version="0.1.0"
)

app.include_router(api.router, prefix="/api")
# 挂载图片路径，本地路径 /home/yangxuzheng/Workplace/fastapi/images 可以通过 localhost:8080/images 访问
app.mount("/images", StaticFiles(directory="/home/yangxuzheng/Workplace/fastapi/images"), name="images")
