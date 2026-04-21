# 資料庫管理 (SQLite 去重與儲存)，記憶發?送過的文章
#Python 內建的輕量級資料庫 SQLite，優點是不需要安裝額外軟體，它會直接生成一個檔案（.db），非常適合個人專案或中小型應用
#建立兩張資料表
#1.sent_articles（去重紀錄表）：只存網址與處理時間，每次抓到新文章先來這裡比對
#2.article_content（對話記憶表）：存入新聞的標題、全文與摘要，未來當您在 LINE 追問詳細內容時，系統才能從這裡撈取資料供 LLM 參考（RAG 架構雛形）

import sqlite3
from datetime import datetime

#設定資料庫名稱(執行後會自動產生此檔)，全域變數（常數）
#以後你想換個名字，只要改這一行，全程式的連接都會跟著改，這符合軟體開發的 DRY (Don't Repeat Yourself) 原則。
#全大寫代表它是一個常數（Constant），也就是說這個名字在整個程式運行期間都不應該被改變。
DB_NAME="ai_news.db"

def init_db():
    '''初始化資料庫，建立所需的資料表'''
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    #建立"去重"用的資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_articles(
             url TEXT PRIMARY KEY ,
            sent_at DATETIME          
                   )
''')
    #建立"儲存文章內容"的資料表(供未來line bot對話檢索用)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS article_content(
                url TEXT PRIMARY KEY,
                title TEXT ,
                   full_text TEXT,
                   summary TEXT       
                   )
''')
    
    conn.commit() #儲存寫入硬碟
    conn.close() #關掉，以釋放電腦資源

def check_if_sent(url:str)->bool:
    '''檢查該網址是否已處理過或發送'''
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    cursor.execute('SELECT 1 FROM sent_articles WHERE url = ?',(url,))
    #SELECT 1：這是在問：「資料庫裡有沒有這筆資料？」有的話請給我一個 1。這比叫資料庫把整行資料讀出來更快。
    #WHERE url = ?：這是一個佔位符。千萬不要直接把網址填進 SQL 字串，否則會遇到 SQL 注入攻擊（資安隱患）。
    #(url,)：這是 Python 的語法细节。在 execute 裡，參數必須包成一個元組（Tuple），即使只有一個東西，後面也要加逗號。

    result=cursor.fetchone()
    #.fetchone() 是叫作業員去拿「一筆」結果。

    conn.close()

    #如果result 有抓到資料，代表處理過了回傳True
    #如果拿得到東西（不是空的），就代表這網址之前存過了，回傳 True。
    return result is not None

def save_article(url:str,title:str,full_text:str,summary:str):
    '''將處理完的文章存入資料庫'''
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    #.strftime(...)：格式化字串
    now=datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    #寫入去重表
    #「請幫我把這篇文章的網址（url）和現在的時間（now）存進『已發送清單』裡。如果這篇文章之前已經存過了，就直接跳過它，不用告訴我，繼續執行後面的程式就好。」
    #INSERT INTO sent_articles：嘗試將新資料寫入名為 sent_articles 的資料表。
    #OR IGNORE：這是最關鍵的部分。如果在寫入時遇到了「衝突」（例如 url 欄位被設定為 PRIMARY KEY 或 UNIQUE，且資料庫裡已經存在相同的 URL），系統會直接忽略這條指令，不會報錯，也不會中斷程式執行。
    #(url, sent_at)：指定要插入資料的欄位名稱。
    #VALUES (?, ?)：這裡的 ? 稱為 「佔位符」（Placeholder）
        #為了防止 SQL 注入攻擊 (SQL Injection)。透過 ?，資料庫驅動程式會自動處理特殊字元，確保傳進去的資料只會被當成單純的「數值」處理，而不會被誤認為是「SQL 指令」。
    #資料傳遞：, (url, now)
        #傳遞給 execute 方法的第二個參數，格式必須是一個 元組 (Tuple)：
        #第一個 ? 會被對應填入變數 url 的內容。
        #第二個 ? 會被對應填入變數 now 的內容（通常是時間戳記）
            #小提醒：即使只有一個變數要傳入，也必須寫成元組的形式（例如 (variable,)），否則 Python 會報錯。
    cursor.execute('''
        INSERT OR IGNORE INTO sent_articles(url,sent_at)
        VALUES(?,?)           
''',(url,now))
    

    #寫入內容記憶表
    cursor.execute('''
        INSERT OR IGNORE INTO article_content(url,title,full_text,summary)
        VALUES(?,?,?,?)
''',(url,title,full_text,summary))
    
    conn.commit()
    conn.close()

#新增檢索功能
def get_article_content_by_url(url:str):
    '''用主鍵網址去資料庫撈出儲存的文章全文
    回傳: Dict 或 None
    '''
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    cursor.execute('SELECT title , full_text FROM article_content WHERE url=?' ,(url,))
    result=cursor.fetchone()

    conn.close()
    if result:
        ## 因為只選了兩個欄位，所以索引是 0 和 1
        return {"title":result[0],"full_text":result[1]}
    return None

#----本地測試區塊----
if __name__=="__main__":
    print("---測試SQLite資料庫模組---")

    #1.初始化資料庫(若不存在會自動建立)
    print("正在初始化資料庫...")
    init_db()
    print("資料庫初始化完成")

    #2.假資料測試
    test_url="https://example.com/fake-ai-news" 
    test_title="測試用新聞標題"
    test_full_text="這是一段測試用的新聞全文內容......."
    test_summary="這是測試用的AI生成的文章摘要"

    #3.第一次檢查(預期結果因為還沒存過，所以會是False)
    is_sent_before=check_if_sent(test_url)
    print(f"檢查該網址是否處理過:{'已處理過'if is_sent_before else '未處理，為全新文章'}")

    if not is_sent_before:
        #4.儲存資料
        print("正在儲存文章...")
        save_article(test_url,test_title,test_full_text,test_summary)
        print("儲存成功")
    
    #5.再次檢查(預期結果:因為剛剛存過所以是True)
    is_sent_after=check_if_sent(test_url)
    print(f"第二次檢查:{'已處理過' if is_sent_after else'未處理過，全新文章'}")




    
