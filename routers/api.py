from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from schemas.request_schemas import *
from schemas.response_schemas import *
from services import image_to_text, query_answer

router = APIRouter()

@router.post("/image2latex", response_model=LatexResponse)
async def upload_image(file: UploadFile = File(...)):
    text, image = await image_to_text.run_model(file)
    return LatexResponse(text=text, image=image)

@router.post("/query", response_model=AnswerResponse)
def query(req: QueryRequest):
    think,answer = query_answer.answer(req.latex, req.query)
    return AnswerResponse(answer=answer,think=think)

@router.post("/query-stream", response_model=AnswerResponse)
def query_stream(req: QueryRequest):
    try:
        # 获取生成器对象
        stream_generator = query_answer.answer(req.latex, req.query, stream=True)
        
        # 创建并返回流式响应
        return StreamingResponse(
            content=stream_generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用Nginx代理缓冲
            }
        )
    except Exception as e:
        # 处理初始化阶段的错误
        raise HTTPException(status_code=500, detail=str(e))
