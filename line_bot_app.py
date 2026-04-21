 # LINE Bot 伺服器 (接收對話與推播)#更新程式碼至最新的 LINE Bot SDK v3

#去 LINE Developers Console 申請一個 LINE Bot 頻道，並取得兩個關鍵金鑰
    #Channel Access Token：這是您的機器人發送訊息的通行證
    #Your User ID：一串專屬於您的 LINE 帳號 ID（注意不是 LINE ID，是在開發者後台取得的 User ID），這樣機器人才知道要「主動把訊息推給誰」。
#安裝 LINE SDK 
    #pip install line-bot-sdk
#安裝 Flask 套件
    #pip install flask
#新增 Channel Secret:在接收 LINE 訊息時，我們需要驗證訊息真的是從 LINE 官方傳來的（避免惡意攻擊）。請到您的 LINE Developers 後台，找到 Channel Secret（通常在 Basic settings 分頁裡），然後把它加到您的 config.py 中
#引入 Flask，並建立了一個 /callback 路由來專門接收 LINE 傳來的訊息
from flask import Flask,request,abort

#1.實作主動推播的函式 send_daily_push，把標題、摘要與原文連結組合起來發送
#----舊版---
# from linebot import LineBotApi ,WebhookHandler
# from linebot.models import TextSendMessage ,TextMessage ,MessageEvent
# from linebot.exceptions import InvalidSignatureError
#---全新更新為新版V3---
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage as V3TextMessage,
    PushMessageRequest
)
from linebot.v3.webhooks import MessageEvent,TextMessageContent

#閱讀全文後回答功能:
import re #python 內建的正規表達式模組，用來抓取網址
from database import get_article_content_by_url
from llm_processor import generate_detailed_reply

## 載入 config.py 裡的設定
from config import LINE_CHANNEL_ACCESS_TOKEN,MY_LINE_USER_ID ,LINE_CHANNEL_SECRET

#GitHub Actions 搭配 API 喚醒#在 Flask (Render 伺服器) 新增一個「觸發用 API」

import threading

from database import init_db

init_db()


app=Flask(__name__)

#---0421新增
# 在 line_bot_app.py 加入以下內容


@app.route("/trigger-job", methods=['GET', 'POST'])
def trigger_job():
    from main_daily_job import run_pipeline # 確保你有將主程式邏輯封裝成函式
    # 簡單的安全性檢查（選配）：可以從環境變數讀取一個 KEY
    # if request.args.get('key') != "YOUR_SECRET_KEY":
    #     return "Forbidden", 403
    
    try:
        print("開始執行定時抓取任務...")
        run_pipeline()# 呼叫你原本在 main_daily_job.py 寫好的邏輯
        return "Job Completed Successfully!", 200
    except Exception as e:
        print(f"執行失敗: {e}")
        return f"Error: {str(e)}", 500
     #0421新增---

# 在 Flask app 啟動前先跑一次，確保表格一定存在



#初始化Line Bot API
#line_bot_api=LineBotApi(LINE_CHANNEL_ACCESS_TOKEN) #舊
#v3更新版:
configuration=Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler=WebhookHandler(LINE_CHANNEL_SECRET)

#接收Line訊息的webhook路由
@app.route("/callback",methods=["POST"])
def callback():
    #取得Line傳來的簽章
    signature=request.headers['X-Line-Signature']
    #取得請求的純文字內容
    body=request.get_data(as_text=True)

    try:
        #將訊息交給headler處理
        handler.handle(body,signature)
    
    except InvalidSignatureError:
        print("簽章驗證失敗，請檢查Channel Secret")
        abort(400) #用來立即中斷請求並回傳 HTTP 400 Bad Request（錯誤的請求） 給用戶端的函式。
    return'OK'

#接收定時排程觸發的 API 路由
@app.route("/trigger-daily-news",methods=['Get'])
def trigger_news():
    from main_daily_job import run_pipeline
    print("收到定時排成觸發請求，準備開始每日新聞管線..")
    # 使用 threading 在背景執行，避免抓新聞太久導致 Render API 逾時 (Timeout)
    threading.Thread(target=run_pipeline).start()

    return"新聞處理管線已成功在背景觸發啟動!",200

#處理使用者的文字訊息(被動回覆)
#@handler.add(MessageEvent,message=TextMessage) #舊
@handler.add (MessageEvent,message=TextMessageContent)

def handle_message(event):
    user_message=event.message.text
    print(f"收到來自LINE訊息:{user_message}")


    # #目前先做簡單的鸚鵡學舌回應，確認連線成功
    # #未來再加入RAG邏輯
    # reply_text=f"謝謝你的訊息:[{user_message}]\n\n(...對話功能建置中...)"
    # # line_bot_api.reply_message(
    # #     event.reply_token,
    # #     TextSendMessage(text=reply_text)
    # # ) #舊
    # #v3更新 呼叫reply API
    # with ApiClient(configuration) as api_client:
    #     line_bot_api=MessagingApi(api_client)
    #     line_bot_api.reply_message_with_http_info(
    #         ReplyMessageRequest(
    #             replyToken=event.reply_token,
    #             messages=[V3TextMessage(text=reply_text)]
    #         )
    #     )

    #使用正則表達式尋找使用者訊息中的網址(http://或https:// 開頭)
    #urls=re.findall(r'(https?://\S+)',user_message) #會回傳一個 list，# 直接把 list 傳進去SQLite會報錯
    #r'...'：代表這是一個「原始字串（Raw String）」，告訴 Python 不要處理裡面的反斜線。
        #( ... )：擷取群組。代表我們要把括號內匹配到的東西「抓出來」。
        # https?：匹配開頭為 http 的文字，? 代表 s 是可有可無的（同時支援 http 或 https）。
        # ://：精確匹配網址必備的符號。
        # \S+：
        # \S（大寫 S）代表非空白字元（也就是數字、字母、符號）。
        # + 代表一個以上。
        # 白話文：一直抓取直到遇到「空白鍵」或「換行」為止。
    urls=re.findall(r'(https?://\S+)',event.message.text)
    if urls:
        target_url=urls[0] #取出第一個網址字串 (關鍵：加上 [0])
        print(f"偵測網址，正在資料庫中搜尋:{target_url}")

        #動作1:檢索資料庫(Retrieval)
        article=get_article_content_by_url(target_url) #傳入資料庫查詢 (這時傳入的是字串，不會報錯)

        if article:
            print(f"找到文章:{article['title']}，AI正在思考中..")
            #動作2:增強生成(Augmented Generation)
            reply_text=generate_detailed_reply(article['full_text'],user_message)
        else:
            reply_text="抱歉，在我的資料庫中找不到此篇全文，或已過期"
    else:
        #如果使用者未提供網址，告知提問方法
        reply_text=(
            "請在訊息中附上你想追問的[新聞連結]，並寫下你的問題，我才能幫你解答喔!\n\n" 

            "範例:\n這篇的技術細節是什麼? https://example.com/ai-news"
        )
    #動作3:將生成的解答回覆給使用者
    with ApiClient(configuration) as api_client:
        line_bot_api=MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[V3TextMessage(text=reply_text)]
            )
        )

#主動推播功能
def send_daily_push(news_list):
    '''
    接收整理好的新聞清單，並主動發送到指定的line帳號
    news_list格式為:[{'tiele':'...','summary':'...','url':'...'}]
    '''

    if not news_list:
        print("今日無適合的推播新聞")
        return
    
    #組合推播訊息的文字內容
    message_text="🚀今日專屬AI新聞快報\n\n"

    for i, news in enumerate(news_list,1):
        message_text+=f"🤖第{i}則新聞:\n{news['title']}\n\n"
        message_text+=f"💡摘要:\n{news['summary']}\n\n"
        message_text+=f"🔗連結:\n{news['url']}\n\n"
        message_text+="\n\n"+"-"*15+"\n\n"
    #message_text+="\n可詢問哪一篇的詳細內容，將由AI助手替你深入解說"

    try:
        #使用push_message主動發送訊息給特定的User ID
        # line_bot_api.push_message(
        #     MY_LINE_USER_ID,
        #     TextSendMessage(text=message_text)
        # )#舊
        #v3更新版 呼叫push api:
        with ApiClient(configuration) as api_client:
            line_bot_api=MessagingApi(api_client)
            line_bot_api.push_message(
                PushMessageRequest(
                    to=MY_LINE_USER_ID,
                    messages=[V3TextMessage(text=message_text)]
                )
            )
        print("Line推播成功")
    except Exception as e:
        print(f"Line推播失敗，{e}")

#啟動Flask伺服器
if __name__=="__main__":
    print("啟動webhook伺服器，port 5001")
    app.run(port=5001)
#當您在終端機執行 python line_bot_app.py 時，
# 它會啟動一個本地伺服器（預設網址是 http://127.0.0.1:5001）。這代表伺服器已經準備好接收訊息了
#但是，LINE 的官方伺服器是在外網，它無法直接把訊息傳進您電腦的 127.0.0.1 內部網路
# 這就是為什麼本地端穿透測試 (ngrok) 非常重要。
# #我們需要用 ngrok 產生一組臨時的 HTTPS 網址，填入 LINE 後台的 Webhook URL 欄位，這樣這條「對話橋樑」才算真正打通

#---本地測試主動推播系統---
# if __name__=="__main__":
#     print("Line主動推播測試..")
#     test_news=[
#         {
#             'title':'Google Gemini模型大進步',
#             'summary':'Gemini 結合NotebookLM 新功能...',
#             "url":"https://example.com/"
#         }
#     ]
#     send_daily_push(test_news)
