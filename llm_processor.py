  # LLM 核心 (判斷喜好 + 摘要 + 追問)
#用「語意 + 角色設定」來判斷喜好的核心大腦
#撰寫 check_interest 的判斷邏輯。這段程式碼會將您的「Persona（個人喜好）」與新聞標題結合，並嚴格要求 LLM 輸出 JSON 格式（例如 {"is_interested": true/false, "reason": "..."}），這樣能讓 Python 程式穩定地接手後續的判斷邏輯
#API 重試機制（Retry）：我們將 client.models.generate_content 與 json.loads 解析過程都包在 try...except 與 for attempt in range(3): 裡面。未來如果遇到網路不穩、Gemini 伺服器短暫異常，或是 AI 偶爾不聽話回傳了壞掉的 JSON 格式，程式都會自動休息 3 秒後再試一次，最高嘗試 3 次，大大提升了您系統的穩定度。
#批次處理保護（Rate Limiting）：在測試迴圈的最後加上了 time.sleep(2)。當您未來將 fetch_news.py 抓回來的幾十篇新聞連續丟進來判斷時，這個暫停能避免您的免費 API 額度瞬間觸發「每分鐘請求次數上限」。

#舊版#pip install google-generativeai #使用google gemini當LLM #移除指令pip uninstall google-generativeai -y
#新版 pip install google-genai


import json
import time #引入time模組 來暫停時間，避免頻繁API要求而遭封鎖
from google import genai
#import google.generativeai as genai #舊版
#from config import GEMINI_API_KEY,SYSTEM_PERSONA,GEMINI_MODLE
from config import SYSTEM_PERSONA

import os


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODLE= os.getenv('GEMINI_MODLE')



#初始化客戶端(設定Gemini API KEY)

client=genai.Client(api_key=GEMINI_API_KEY)

def check_interest(title:str):
    '''
    將新聞標題給LLM，判斷是否符合個人喜好，以是否推薦此篇新聞。並順便翻譯標題為繁體中文。
    回傳值:(translated_title:str,is_interested:bool
    '''
    #回傳值:(translated_title:str,is_interested:bool,reason:str)

   

    prompt=f"""
    {SYSTEM_PERSONA}

    請根據以下新聞標題，判斷此新聞是否符合使用者喜好，並順便翻譯標題為繁體中文。
    新聞標題:{title}
    請務必嚴格遵守以下格式回傳JSON，不要包含其他任何多餘文字或Markdown符號:
    {{
        "translated_title":"請這個標題翻譯成流暢的繁體中文(若原本為中文則直接印出即可)",
        "is_interested":true/false,
        }}
    """
    #"reason":"簡短15字內解釋為什麼"

  #最多三次的重試機制
    for attempt in range(3):
      try:
          response=client.models.generate_content(
              model=GEMINI_MODLE,
              contents=str(prompt)
          )
          #clean_text=response.text.strip().replace('```json','').replace('```','').strip()
          #更精簡寫法:
          clean_text=response.text.replace("json","").strip("` \n")
          #replace("json", "")`: 把文字中間的 `json` 刪掉(替換成空字串)。
          #`strip("` \n")`: 同時把左右兩端的 反引號 (`)、空格、換行 (\n)全部一次剪乾淨。
          result=json.loads(clean_text) ## 加上 s，代表 Load String
          #json.load() (沒有 s)：它是用來讀取「檔案」的
          #json.loads() (有 s)：這個 s 代表 String（字串）。它是專門用來處理「字串格式的 JSON」。

          #安全取出翻譯過的標題，若AI漏掉則預設回傳原標題
          translated_title=result.get("translated_title",title)
          is_interested=result.get("is_interested",True)
          #去 result（AI 回傳的 JSON 字典）裡找 "is_interested" 這個標籤。
          #如果找到了：就直接把裡面的值（可能是 True 或 False）存進 is_interested 變數裡。
          #如果沒找到：AI 有時候會漏掉欄位，或者回傳格式錯誤。這時如果不用 .get() 程式會崩潰；
          # 用了 .get("...", False)，程式就會說：「既然沒寫，那我就預設你沒興趣吧！」並把值設為 False，讓程式繼續執行。

          #reason=result.get("reason","未提供理由")
          


          #若成功獲取並解析結果，直接打斷迴圈 
          # #return 不只是「回傳結果」，它同時也是這份工作（函數）的「終止符」
          #第一次嘗試：如果成功了，執行到 return，員工就回家了。迴圈的第二次、第三次就不會發生。
          return translated_title,is_interested 
        #return translated_title,is_interested ,reason
      except Exception as e:
        print(f'第{attempt+1}次失敗:{e}')
        if attempt <2: #如果不是最後一次，就先等待一下再重試 #迴圈是 range(3)（也就是 0, 1, 2）#attempt 為 2 時（最後一次失敗）
            #在進行任何「耗時」的操作（如等待、下載、運算）之前，先給使用者一個提示，可以大幅降低使用者的焦慮感。
            #先印再通知
          print("休息3秒後再重試")
          time.sleep(3)
        else:
            print("已嘗試三次，跳過此篇新聞")
            return False,"解析失敗或API錯誤"
            #回傳 False 的作用：就像是給主程式一張「查無此人」的通知單，雖然沒查到，但至少格式是對的，主程式能看懂。
            #在函式的設計（Docstring 註解）中規定了它要回傳一個布林值 (bool) 和一個字串 (str)
            #保持「回傳類型的一致性」


#生成摘要函示
def generate_summary(content:str)->str:
    '''
    將抓取到的完整新聞內容給LLM生成10句內的摘要
    回傳: 摘要字串
    '''

    prompt=f"""
    請幫我閱讀以下這篇新聞的全文內容，並寫出一段[10句以內]重點摘要。
    請著重在說明這項技術或新聞[為什麼值得關注]或是[它的核心應用場景]，並且使用繁體中文。(加上多點表情符號以便好閱讀)

    新聞全文:{content}
    """
    #嘗試最多3次的重試機制
    for attempt in range(3):
        try:
            print("LLM生成摘要中")
            response=client.models.generate_content(
                model=GEMINI_MODLE,
                contents=prompt
          )
            #直接回傳生成摘要的文字
            return response.text.strip()
        except Exception as e:
            print(f"生成摘要嘗試第{attempt+1}次，失敗原因:{e}")
            if attempt<2:
                print("休息3秒後準備重試...")
                time.sleep(3)
            else:
                print("已重試三次，無法生成摘要")
                return"發生錯誤，無法生成摘要"

#詳細解答功能
def generate_detailed_reply(full_text:str,user_question:str)->str:
    '''
    當使用者追問細節時，會將[全文和使用者提問]，交給LLM來生成詳細解答
    '''

    prompt=f'''
    你是一位專業AI科技新聞助手，請你根據以下新聞全文，來回答使用者的問題提問追加。
    請盡量以淺顯易懂好理解，且繁體中文的方式來回答，並控制在200字以內(可以加上多點表情符號以便好閱讀)。
    若使用者的問題超出全文的範圍，請溫柔提醒使用者:文章內沒有相關的解答。切勿自行胡亂回答。

    【新聞全文】:
    {full_text}

    【使用者的提問】:
    {user_question}

'''
    for attempt in range(3):
        try:
            print("LLM正在思考詳細問答中...")
            response=client.models.generate_content(
                model=GEMINI_MODLE,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"詳細回覆生成第{attempt+1}次，{e}")
            if attempt <2:
                time.sleep(3)
            else:
                return f"生成詳細回覆發生問題:{e}"
#本地端測試喜好篩選
# if __name__=="__main__":
#        #給測試資料試試看
#        test_titles = [
#         "OpenAI 推出全新 GPT-5.7 模型，大幅提升 API 推理速度與視覺能力",
#         "微軟推出語音辨識、語音生成與圖像生成 MAI 模型",
#         "教學：如何使用 Python 與 FastAPI 建立 RAG 檢索增強生成系統",
#         "美超微走私案最新進展：共同創辦人廖益賢與外包商孫廷瑋不認罪",
#         "矽谷巨頭用裁員換 GPU、用監管卡位：AI 軍備競賽，關上通往新創和民意的門",
#         "鴻海 3 月營收寫同期新高，外資看好 AI 機櫃續撐第二季",
#         "Anthropic 年化營收逾 300 億美元，攜手 Google、博通擴大採用下一代 TPU"
#     ]
#        print("測試LLM篩選標準中")
#        for i,t in enumerate(test_titles,1):
#            is_interested,reason=check_interest(t)
#            print(f'標題{t}')
#            print(f"判斷結果:{'有興趣' if is_interested else '略過'}")
#            print(f'理由{reason}')
#            print('-'*50)

#            #迴圈中抓取每一篇新聞發送給AI後，休息一下，最後一篇就不用等
#            if i<len(test_titles):
#                print("休息兩秒，避免頻繁呼叫API")
#                time.sleep(2)


#本地端測試篩要生成:
if __name__=="__main__":
    print("測試摘要生成功能\n")

    sample_full_text='''
Gemini 過往回應大多只是文字和圖像，現在 Gemini 提供模擬功能，幫助使用者更理解自己向 Gemini 提出的問題。無論是模擬分子旋轉還是模擬複雜的物理系統，只需要輸入提示詞，即可進行深入探索，並能輸入不同數值以即時改變模擬結果。

比方說，請 Gemini 建立一個月球繞地球運行的模擬，因此它會生成一個可互動的 3D 模型，提供多種操作方式，像是有調整月球運行速度的滑桿，還有一個按鍵可隱藏代表軌道路徑的線條，以及一個按鍵可暫停月球繞行地球的模擬。

這項更新發表幾週前，Anthropic 為 Claude 加入生成圖表以及其他互動式視覺內容的能力，而 OpenAI 也為 ChatGPT 新增可生成數學與科學概念視覺化的功能，如今 Gemini 使用者可輸入提示詞並選擇「Pro」模型選項，就能生成互動式 3D 模擬。
'''

    summary_result=generate_summary(sample_full_text)
    print('AI摘要如下:\n')
    print(summary_result)
