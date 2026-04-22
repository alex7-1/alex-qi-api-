# Alex Qi · 报价截图识别后端

## 部署到 Railway（5分钟）

### 第一步：上传代码
1. 去 [github.com](https://github.com) 新建一个 repository（名字如 `alex-qi-api`）
2. 把这个文件夹里的三个文件上传进去：
   - `main.py`
   - `requirements.txt`
   - `railway.toml`

### 第二步：部署到 Railway
1. 去 [railway.app](https://railway.app) 注册（用 GitHub 账号登录最方便）
2. 点 **"New Project"** → **"Deploy from GitHub repo"**
3. 选刚才创建的 repository
4. Railway 会自动识别并开始部署

### 第三步：设置 API Key
1. 在 Railway 项目页面，点 **"Variables"**
2. 点 **"Add Variable"**
3. 名字填：`ANTHROPIC_API_KEY`
4. 值填：你的 Anthropic API Key（去 console.anthropic.com 获取）
5. 点 Save，Railway 会自动重启

### 第四步：获取你的后端地址
部署完成后，Railway 会给你一个地址，格式类似：
```
https://alex-qi-api-production.up.railway.app
```

### 第五步：更新报价卡
把报价卡 HTML 里的后端地址改成你的 Railway 地址：
在 `alex_qi_quote_card.html` 里搜索 `YOUR_BACKEND_URL`，替换成你的 Railway 地址。

---

## API 接口

### POST /api/parse-screenshot
上传截图，返回识别到的合同数据。

**请求**：multipart/form-data，字段名 `file`，值为图片文件

**返回示例**：
```json
{
  "success": true,
  "data": {
    "supplier": "eprimo",
    "contract": "eprimoStrom PrimaKlima mit Bonus",
    "monthly": "52.57",
    "yearly": "630.84",
    "arbeitspreis": "28.40",
    "grundpreis": "204.85",
    "bonus": "100",
    "has_bonus": true,
    "duration": "12",
    "guarantee": "12",
    "tags": "100€ 新客优惠 / 100% 绿电 / 12个月保价",
    "firstyear": "530.84"
  }
}
```

### GET /
健康检查，返回 `{"status": "ok"}`
