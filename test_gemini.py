from google import generativeai as genai

# 用你申请到的 API Key 替换下面内容
genai.configure(api_key="你的_API_Key")

response = genai.generate_text(
    model="models/gemini-2.5-pro",
    prompt="你好，Gemini 2.5 Pro！",
    max_output_tokens=50
)

print("AI 回复:", response.text)
