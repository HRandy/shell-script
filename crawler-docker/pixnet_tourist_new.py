
# coding: utf-8

# In[2]:

###  痞客邦旅遊 "最新文章"  ###

import requests as r
from bs4 import BeautifulSoup
import json
import time
from Queue import Queue
from threading import Thread
from datetime import datetime


######### 開啟 url比對資料庫
try:
    with open('pixnet_url_database.json', 'rb') as hi:
        pixnet_database_list = json.load(hi)
        print "open exsisting pixnet_url_database_list..."
        hi.close()        
except Exception as e:    
    pixnet_database_list = []
    print "create a new pixnet_url_database_list to append urls used"


box_list = []

####   爬蟲實施抓取網頁
def worker():    
    while not queue.empty():
        url=queue.get()
        crawler(url) 

        
####   爬蟲程序            
def crawler(url): 

    res = r.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'lxml')
    aboxs = soup.select_one('ol.article-list').select('li')

    for abox in aboxs:
        load_url = abox.select_one('h3').select_one('a')['href']
        if load_url in pixnet_database_list:
            continue
            print "this url has loaded"        
        
        try:
            dict3 = {}
            dict3['title'] =abox.select_one('h3').select_one('a').text
            dict3['url'] = abox.select_one('h3').select_one('a')['href']
            dict3['author'] = abox.select_one('span.meta').select_one('a').text
            dict3['date'] = abox.select_one('span.meta').text.strip().encode('utf-8').split('於')[1].split(' ')[1]
            dict3['reply'] = abox.select_one('span.meta').text.encode('utf-8').split("留言")[1].strip().split('(')[1].split(')')[0]
            box_list.append(dict3)
            pixnet_database_list.append(load_url)
            #print "done" #####測試有無執行到
        except Exception as e: 
            print e     

        
####   創建一個 Queue
global queue
queue = Queue()       
        

#### 頁數 URL 放進 Queue   
try:    
    a = 1  ##此不能更改
    b = 700 ##設定最大值為700頁
    URL = "https://www.pixnet.net/blog/articles/category/29/new/{}"
    for page in range(a, b):    
        page_url=URL.format(page)
        queue.put(page_url)

except Exception as e:    
    print "page url err"    
    

#s1 = datetime.now() ####### 起始時間

##########   啟動THREAD
threads = map(lambda i: Thread(target=worker), xrange(3))
map(lambda th: th.start(), threads)
map(lambda th: th.join(), threads)


s2 = datetime.now() ####### 結束時間
#print "All  Finish "+str(s2-s1)+"!!" ####### 總共爬取資料耗費時間



time = time.strftime("%Y%m%d")
########## 新增 url到比對資料庫
try:
    pixnet_database = json.dumps(pixnet_database_list, ensure_ascii=False)
    with open('pixnet_url_database.json', 'w') as a:
        a.write(pixnet_database.encode('utf-8'))            
        a.close() 
except Exception as e:
    print "database story err"


##########   存檔
try:
    
    traveljson = json.dumps(box_list, ensure_ascii=False)
    with open('pixnetTouist_new_{}.json'.format(time), 'w') as a:
        a.write(traveljson.encode('utf-8'))
        print 'case close'
except Exception as e:
    print "content story err"


# In[ ]:



