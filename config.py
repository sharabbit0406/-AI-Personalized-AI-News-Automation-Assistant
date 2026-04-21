# 部署版設定檔 (放 API Keys、RSS 網址、 Persona 提示詞)
import os
# ==========================================
# 1. API 金鑰與 LINE 設定 (改由系統環境變數讀取)
# ==========================================
# os.getenv 會自動去 Render 的 Environment Variables 抓取對應的值
GEMINI_API_KEY= os.getenv("GEMINI_API_KEY")
GEMINI_MODLE=os.getenv("GEMINI_MODLE")

LINE_CHANNEL_ACCESS_TOKEN=os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
MY_LINE_USER_ID=os.getenv("MY_LINE_USER_ID")
LINE_CHANNEL_SECRET=os.getenv("LINE_CHANNEL_SECRET")

#2.資料來源rss
RSS_FEEDS=[
"https://technews.tw/category/it/ai/feed/",
#"https://technews.tw/tn-rss/",
#"https://huggingface.co/blog/feed.xml",
#"https://blog.google/technology/ai/rss/",
"https://venturebeat.com/category/ai/feed/",

]


#3.ai判斷大腦設定(Persona)
# 如果未來喜好變了 (例如想開始看某個特定框架)，只要改這裡就好
SYSTEM_PERSONA='''
你是一個篩選AI科技新聞的助手，篩選使用者感興趣的新聞給使用者。
使用者喜好:非常關注各種LLM(大型語言模型ChaptGPT、Gemini、Claude、Claude code、NotebookLM、OpenClaw...)、和各大AI巨頭(OpenAI、Google、Anthropic、Meta...)相關的新聞，以及AI應用技術(RAG、MCP、API、prompt、vibe coding...，或是新推出的技術)，和模型及各AI公司的進展，還有任何跟AI工程師或AI工作有關的新聞。
最重要喜歡的是AI有關心理健康(聊心事等等)、人腦大腦有關的新聞。
不感興趣:AI記憶體、電力、國安、宇宙、金融、政治、晶片、股票等等的

'''
