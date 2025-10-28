from google import generativeai as genai

# 配置 API Key
genai.configure(api_key="AIzaSyDnTqJxkejtVKH7qpIcDGSqnl3sSb-gTCY")

# 初始化模型（推荐使用 gemini-1.5-flash）
model = genai.GenerativeModel("gemini-2.5-flash")

# 生成回复
response = model.generate_content("你好，请介绍一下你自己。")

# 输出结果
print(response.text)
