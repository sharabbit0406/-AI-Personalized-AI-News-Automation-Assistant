# 抓取新聞來源
#pip install feedparser
#在這個階段，我們不需要寫複雜的網頁爬蟲，而是使用 feedparser 這個強大的 Python 套件來解析各大科技媒體的 RSS 訂閱源。它能幫我們把不同來源的新聞整理成一致的格式，方便後續丟給 AI 處理

import feedparser
from config import RSS_FEEDS

#免費RSS來源


def get_latest_news(max_per_feeds=10):
    '''
    抓取指定的RSS來源，並整理成統一格式。
    回傳格式:[{'title':'...','url':'...']

    '''
    #回傳格式:[{'title':'...','url':'...','summary':'...'}] 捨棄摘要
    
    news_list=[]

    for feed_url in RSS_FEEDS:
        [print(f"正在抓取來源:{feed_url}")]

        #使用feedparser 解析RSS網址
        feed=feedparser.parse(feed_url)

        #取出該來源前幾篇最新文章(先少量測試)
        for entry in feed.entries[:max_per_feeds]:  #.entries 就是拿出包裹裡的**「文章列表」**（它是一個 List，也就是清單）。「從頭開始拿，拿到第 3 個就停」
            title=entry.get('title','無標題')
            url=entry.get('link','無連結')
            #entry 就是你從箱子裡拿出來的「那一篇文章」。在 Python 中，這篇文章的資料結構通常是一個字典 (Dictionary)。
            #字典的概念就像是一本個人檔案，裡面會有「標籤（Key）」和相對應的「內容（Value）」，例如：{'title': '今天天氣很好', 'link': 'http://...'}。
            #我們把這兩行拆開來看：
            # 1. title = entry.get('title', '無標題')
            # 這行的白話文是：「去這篇文章（entry）裡面找『標題（title）』的內容，如果找不到，就當作它是『無標題』。」
            # entry.get(...) 的妙用：
            # 在 Python 字典中找東西，最直覺的寫法其實是 entry['title']。但這種寫法有個致命傷：如果這篇文章剛好壞掉了，裡面沒有 'title' 這個標籤，程式就會直接當機（報錯）並停止運作！
            # 預設值機制：
            # 使用 .get('標籤名稱', '預設值') 是一種防呆機制。逗號後面的 '無標題' 就是你設定的「備胎」。當程式找不到文章標題時，它不會崩潰，而是默默地把 title 這個變數設定為 '無標題'，然後繼續順利執行。

            #不同的RSS來源可能會把內文或摘要放在summary或description
            #summary=entry.get('description',entry.get('summary','無摘要內容'))

            #將抓取到的資料整理成字典格式並加入列表
            news_list.append({
                'title':title,
                'url':url,
                #'summary':summary,
            })
    
    return news_list

#本地端測試區塊
if __name__=="__main__":
    print("測試抓取AI新聞")

    #呼叫主函示，取得新聞列表
    latest_news=get_latest_news()
    print(f'\n抓取完成，共取得{len(latest_news)}篇新聞:\n')

    #將抓取到的新聞印在終端機上預覽
    for i,news in enumerate(latest_news,1): #邊數數、邊拿東西。第一個參數 latest_news：這是你裝滿新聞的箱子（清單）。二個參數 1：這是告訴電腦「從 1 開始數」。如果你不寫，預設會從 0 開始。
        #i (Index)：這就是序號。第一次迴圈它是 1，第二次是 2，依此類推。
        #news：這是一篇新聞的完整內容（也就是之前拿到的標題、網址等）。
        print(f'[新聞{i}]{news['title']}')
        print(f'連結:{news['url']}')
        #print(f'原始摘要長度:{len(news['summary'])}')
        print("-"*40)