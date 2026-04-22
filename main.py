import os
import base64
import json
import anthropic
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Alex Qi · 报价截图识别 API")

# CORS — 允许你的报价卡 HTML 从任何地址调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Anthropic 客户端（API Key 从环境变量读取）
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

PROMPT = """请从这张德国电力/网络合同系统截图中提取以下数据，严格以JSON格式返回，不要有任何其他文字：
{
  "supplier": "供应商名称（如 eprimo、E.ON）",
  "contract": "合同名称（完整名称）",
  "monthly": "月费数字（不含优惠，单位欧元，只要数字）",
  "yearly": "年费数字（月费×12，只要数字）",
  "arbeitspreis": "度电价（ct/kWh，只要数字）",
  "grundpreis": "年基础费（欧元，只要数字）",
  "bonus": "新客优惠金额（欧元，只要数字，没有则返回0）",
  "has_bonus": "是否有新客优惠（true或false）",
  "duration": "合同期限（只要数字，单位月）",
  "guarantee": "价格保证期（只要数字，单位月）",
  "tags": "合同亮点标签，用/分隔（如：100€ 新客优惠 / 100% 绿电 / 12个月保价）",
  "firstyear": "首年实付金额（年费减去优惠，只要数字）"
}
如果某个字段在截图中找不到，返回空字符串""。"""


@app.get("/")
def health():
    return {"status": "ok", "service": "Alex Qi 报价截图识别"}


@app.post("/api/parse-screenshot")
async def parse_screenshot(file: UploadFile = File(...)):
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")

    # 读取并转 base64
    img_bytes = await file.read()
    if len(img_bytes) > 10 * 1024 * 1024:  # 10MB 限制
        raise HTTPException(status_code=400, detail="图片太大，请压缩后重试")

    img_b64 = base64.standard_b64encode(img_bytes).decode("utf-8")
    media_type = file.content_type

    # 调用 Claude API
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": img_b64
                        }
                    },
                    {
                        "type": "text",
                        "text": PROMPT
                    }
                ]
            }]
        )
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Claude API 错误: {str(e)}")

    # 解析返回的 JSON
    raw_text = message.content[0].text.strip()
    try:
        clean = raw_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="识别结果解析失败，请重试")

    return JSONResponse(content={"success": True, "data": result})
