# 每日 8 點排程主程式 (串接所有流程)

#抓標題 → 判斷喜好(若True) → 抓全文 → 生成摘要
import time
from fetch_news import get_latest_news
from full_text import fetch_full_text
from llm_processor import check_interest,generate_summary
from database import init_db,check_if_sent,save_article
from line_bot_app import send_daily_push

def run_pipeline():
    print("啟動AI新聞處理管線")

    #動作0:初始化資料庫
    print("▶️檢查並初始化資料庫..")
    init_db()

    #動作1:抓標題
    print("▶️動作1.正在抓取RSS新聞標題...")
    news_list=get_latest_news(max_per_feeds=3)
    print(f"▶️共抓取到{len(news_list)}篇新聞")
    print("-"*50)

    #準備一個空列表，用來收集今日準備推播的新聞
    daily_push_list=[]

    for i , news in enumerate(news_list,1):
        url=news['url']
        print(f"第{i}篇新聞標題:{news['title']}，連結:{news['url']}")
        
        #動作1.5去重機制，在給AI判斷前先檢查資料庫裡是否已存在
        if check_if_sent(url):
            print("▶️發現重複文章，跳過本次處理")
            continue #直接進入迴圈的下一個新聞

        
        #動作2:判斷喜好
        print("▶️2.AI正在判斷喜好...")
        translated_title,is_interested=check_interest(news['title'])
        #translated_title,is_interested,reason=check_interest(news['title'])
        print(f"標題:{translated_title}")
        #print(f"▶️判斷結果:{'有興趣'if is_interested else '沒興趣'}，因為:{reason}")
        print(f"▶️判斷結果:{'有興趣'if is_interested else '沒興趣'}")


        #動作三:有興趣抓全文
        if is_interested:
            print("▶️3.判斷有興趣,正在抓取全文..")
            full_text=fetch_full_text(news['url'])

            if len(full_text)>100:
                print(f"▶️成功抓取全文，共{len(full_text)}字")

                #動作4:生成摘要
                print("▶️4.正在閱讀全文並生成摘要..")
                summary=generate_summary(full_text)
                print("▶️生成最終摘要:")
                print(summary)
                print("\n"+"-"*50+"\n")

                #動作5:寫入資料庫
                #將翻譯過的標題全文摘要存起來，供LINE追問使用，並標記為已發送
                print("▶️5.正在將新聞存入資料庫中...")
                save_article(url,translated_title,full_text,summary)
                print("▶️儲存完成")
                print('-'*50)

                #將成功處理的新聞，按照推播模組的格式加入清單
                daily_push_list.append({
                    'title':translated_title,
                    'summary':summary,
                    "url":url,
                })

                #每天挑選5篇新，收集滿了提早結束迴圈
                if len(daily_push_list)>=5:
                    print("已收集滿5篇文章，停止後續文章處理")
                    break
            else:
                print("▶️全文過短，抓取全文失敗，跳過摘要")
        else:
            print("▶️無興趣跳過摘要")

        #休息2秒，避免API密集呼叫
        time.sleep(2)

    #動作6.執行Line主動推播
    print("▶️ [動作 6] 準備執行 LINE 推播...")
    if daily_push_list:
        print(f"即將推播{len(daily_push_list)}篇文章")
        send_daily_push(daily_push_list)
    else:
        print("今日無感興趣新聞")

    print("整個管線處理完畢!")

if __name__=="__main__":
    run_pipeline()
