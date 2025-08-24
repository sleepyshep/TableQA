# 👨‍💻 环境准备
请根据`environment.yml`文件准备conda环境

# 🎯 模型部署
## 下载模型
从[model_path](https://huggingface.co/sleepyshep/Qwen_TableQA)下载模型

## 使用vllm部署模型
`vllm serve model_path --port 8007 --host 0.0.0.0 --dtype bfloat16 --max_num_seqs 256 --gpu_memory_utilization 0.9 --max-model-len 10000`

# ✒️ 后端接口
启用后端服务

`python -m uvicorn main:app --reload --port 8080`

# 👀 前端界面
启用前端服务

`pnpm install`

`pnpm run serve`
