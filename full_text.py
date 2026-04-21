#抓取新聞全文的爬蟲功能
#pip install requests beautifulsoup4

import requests
from bs4 import BeautifulSoup

def fetch_full_text(url:str)->str:
    '''
    進入指定網頁抓取新聞全文完整內容。
    回傳:抓取到的純文字內容(若失敗則回傳空字串)
    '''

    #設定User-Agent偽裝成一般瀏覽器，避免被阻擋
    #可google"my user agent"，可查到自己電腦的
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    }

    try:
        print(f"正在此抓取全文{url}")
        #發送GET請求網頁獲取HTML，設定10秒timeout 避免一直等待導致程式卡死
        #「我願意花多少時間等對方回應？如果時間到了還沒回，我就不等了（直接報錯）。」
        response=requests.get(url,headers=headers,timeout=10)
        response.raise_for_status() #檢查是否發生HTTP錯誤(例如403、404)
        #raise 是把錯誤丟出來。像是一個品檢員
        #合格了，他就點點頭（什麼都不說，也不會給你新東西）。
        #不合格，他就直接按下「緊急停止按鈕」（拋出報錯），讓程式停下來。

        #使用beautifulsoup解析HTML
        soup=BeautifulSoup(response.text,'html.parser')

        #提取文章內容:通常新聞網站的正文都在標籤<p>內#find_all，抓取「所有」<p> 標籤
        paragraphs=soup.find_all('p')

        #將所有段落文字題取出來，去頭去尾空白，並用換行符號連接
        # #拿掉 HTML 標籤、刪掉網頁中沒意義的空白段落、原本散落在各處的段落，重新組合回一篇完整的文章
        #for p in paragraphs:# 遍歷所有的段落標籤（p 通常是 BeautifulSoup 抓到的 <p> 物件）。
        # if p.get_text().strip() (過濾):
        # 這是一個防呆機制。有些網頁標籤可能是空的（例如 <p></p> 或 <p>  </p>）。strip() 後如果變成空字串，在 Python 中會被視為 False，這樣空的段落就不會被放進清單裡。
        # p.get_text().strip() (加工):
        # get_text(): 只要標籤裡的文字，把 HTML 標籤（如 <a>, <span>）全部拿掉。
        # strip(): 把文字前後多餘的空格、換行符號清乾淨。
        full_text="\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

        #好幾行的寫法
        # cleaned_paragraphs = []
        # for p in paragraphs:
        #     text = p.get_text().strip()
        #     if text:  # 確保不是空字串
        #         cleaned_paragraphs.append(text)
        # full_text = "\n".join(cleaned_paragraphs)

        #若內文太短(可能是抓錯標籤)，簡單的檢查
        if len(full_text)<100:
            print("警告:內文過短，可能該網站有反爬蟲機制")

        return full_text
    except Exception as e:
        print(f"抓取全文時發生問題{e}")
        return""
    
#本地測試區
if __name__=="__main__":
    #測試網頁:
    test_url="https://venturebeat.com/infrastructure/claude-code-costs-up-to-usd200-a-month-goose-does-the-same-thing-for-free"
    print("開始抓取網頁全文")
    
    article_text=fetch_full_text(test_url)
    if article_text:
        print(f"成功抓取到全文，總字數{len(article_text)}")
        print("內文預覽前300字:\n")
        #print(article_text[:300]+"...\n")
        print(article_text)
    else:
        print("抓取失敗或無內容")