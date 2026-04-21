# -AI-Personalized-AI-News-Automation-Assistant
🤖 專案簡介本專案旨在解決「資訊爆炸但時間破碎」的痛點，打造一個能與使用者互動的 自動化 AI 科技新聞助手Line Bot。 
🚀 核心技術亮點：智能篩選：捨棄傳統關鍵字，利用 LLM（Gemini）進行語意分析，**根據使用者偏好**精準過濾新聞。 
高效摘要：自動將長篇原文濃縮為 10 句內的精華，助你 1 分鐘掌握重點。 
RAG 互動追問：結合 SQLite 資料庫與檢索增強生成（RAG）技術，使用者可在 LINE 上針對特定新聞**進行深度對話**，由 AI 根據全文內容提供詳盡解答。 
全自動化流水線：透過 GitHub Actions 設定排程，每日早上 8 點準時將最新資訊推播至 LINE。

-----

# 自動化 AI 科技新聞助手 (Personalized-AI-News-Automation-Assistant)

## 🤖 專案簡介

本專案旨在解決「資訊爆炸但時間破碎」的痛點 。這是一個具備**個人化語意篩選**能力的 AI 新聞機器人，它能每天定時從各大科技媒體抓取資訊，利用 LLM（大語言模型）判斷是否符合使用者興趣，並生成精簡摘要推播至 LINE 。此外，本專案整合了 **RAG (檢索增強生成)** 技術，讓使用者能針對特定新聞進行深度對話追問。

## 🚀 核心功能

  * **智能篩選 (LLM-based Filtering)**：捨棄傳統關鍵字過濾，利用 LLM 進行語意分析，根據預設的個人喜好（Persona）精準篩選新聞 。
  * **精煉摘要**：自動將長篇原文濃縮為 10 句內的繁體中文精華，快速掌握技術重點 。
  * **RAG 互動追問**：結合 SQLite 資料庫，使用者可在 LINE 上對感興趣的新聞網址進行提問，由 AI 讀取資料庫中的完整全文給予詳細解答。
  * **全自動排程推播**：整合 GitHub Actions，每日早上 8:00 準時推播 3-5 則最相關的科技快報 。
  * **自動去重機制**：使用 SQLite 紀錄已發送過的新聞 URL，確保不重複推送相同內容。

## 🛠️ 技術棧

  * **語言**：Python 3.10+
  * **大語言模型**：Google Gemini 2.5 Flash-lite
  * **後端框架**：Flask (搭配 line-bot-sdk-python)
  * **資料庫**：SQLite (用於新聞存儲、去重與 RAG) 
  * **自動化**：GitHub Actions (Cron Job) 
  * **資料來源**：Feedparser (RSS 解析) 

## 📁 專案結構

.
├── main_daily_job.py   # 每日排程入口：抓取 -> 篩選 -> 摘要 -> 推播 
├── line_bot_app.py     # LINE Webhook 伺服器，處理 RAG 對話追問
├── llm_processor.py    # LLM 邏輯處理（篩選、摘要、詳細回答）
├── fetch_news.py       # RSS 新聞抓取模組 
├── database.py         # SQLite 資料庫操作與 RAG 檢索邏輯 
├── config.py           # 環境變數與個人化 Persona 設定 
└── requirements.txt    # 專案依賴套件

## ⚙️ 快速上手

1.  **取得憑證**：
      * 申請 [LINE Developers](https://developers.line.biz/) 帳號並取得 Channel Access Token 與 Secret 。
      *取得 [Google AI Studio (Gemini API)](https://aistudio.google.com/) 的 API Key 。
2.  **環境設定**：
    將 API Key 與相關設定填入 `config.py` 或設定為環境變數 。
3.  **安裝套件**：
    pip install -r requirements.txt
4.  **本地測試**：
   使用 `ngrok` 將本地端 Webhook 暴露，並在 LINE 後台設定 Callback URL。

## 💡 履歷亮點 (Resume Keywords)

  * **LLM-Driven Personalized News Pipeline**：設計並實作基於大模型的個人化新聞流水線。
  * **Semantic Preference Filtering**：利用語意分析取代傳統關鍵字過濾，提升資訊相關度]。
  * **Conversational RAG Implementation**：於通訊軟體實現檢索增強生成，支援針對特定內容的上下文問答。
  * **Cloud-Native Automation**：整合 GitHub Actions 實現 Serverless 定時任務排程。

-----

🤝 聯絡資訊
sharabbit0406@gmail.com
