
# coding: utf-8

# In[9]:

###  痞客邦旅遊全部分類

import requests as r
from bs4 import BeautifulSoup
import json
import time
from Queue import Queue
from threading import Thread
from datetime import datetime


#########   開啟 url比對資料庫
try:
    with open('pixnet_url_database.json', 'rb') as hi:
        pixnet_database_list = json.load(hi)
        print "open exsisting pixnet_url_database_list..."
        hi.close()        
except Exception as e:    
    pixnet_database_list = []
    print "create a new pixnet_url_database_list to append urls used"


    
    
#########   抓第一頁架構


box_list = []
tmp_list = []

URL_PAGE1 = "https://www.pixnet.net/blog/articles/category/29/latest/1"
URL_PAGE2 = "https://www.pixnet.net/blog/articles/category/29/hot/1"
tmp_list.append(URL_PAGE1)
tmp_list.append(URL_PAGE2)

for page_n in tmp_list:
    res = r.get(page_n)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'lxml')

    ###   page1 - 冠軍欄位
    box = soup.select_one('div.featured')
    load_url_1 = box.select_one('a')['href']
    if load_url_1 in pixnet_database_list:
        print "page1 first url has loaded"
    else:
        try:
            dict1 = {}        
            dict1['title'] = box.select_one('a').select_one('img')['alt']  
            dict1['url'] = box.select_one('a')['href']
            dict1['author'] =  box.select_one('span.meta').select_one('img')['alt']
            dict1['date'] = box.select_one('span.publish').text.split(" ")[1]
            dict1['reply'] =  box.select_one('span.publish').text.split(" ")[5].split('(')[1].split(')')[0]
            box_list.append(dict1)
            pixnet_database_list.append(load_url_1)
        except Exception as e:    
            print "page1 first err" 

    ###  page1 - 2~10筆
    tboxs = soup.select_one('ol.article-list').select('li') 
    
    for tbox in tboxs:
        load_url_2 = tbox.select_one('h3').select_one('a')['href']
        if load_url_2 in pixnet_database_list:     #  檢查url 是否重複
            print "page1 2-10 url has loaded"
            continue
        else:    
            try:
                dict2 = {}
                dict2['title'] = tbox.select_one('h3').select_one('a').text
                dict2['url'] = tbox.select_one('h3').select_one('a')['href']
                dict2['author'] = tbox.select_one('span.meta').select_one('a').text
                dict2['date'] = tbox.select_one('span.meta').text.split(' ')[3]
            #     print tbox.select_one('span.meta').text.encode('utf-8').split("留言")[1].strip().split('(')[1].split(')')[0]
                dict2['reply'] = tbox.select_one('span.meta').text.encode('utf-8').split("留言")[1].strip().split('(')[1].split(')')[0]
                box_list.append(dict2)
                pixnet_database_list.append(load_url_2)
                print "page1 2-10 ok"
            except Exception as e:    
                print "page1 2-10 err" 


    
#########   其他頁架構 


###  Queue

global queue
queue = Queue()        

#近期熱門
a = 2   ##此不能更改
b = 700 ##設定最大值為200頁
URL = "https://www.pixnet.net/blog/articles/category/29/latest/{}"
for page_l in range(a, b):    
    page_url_l=URL.format(page_l)
    res_l = r.get(page_url_l)
    soup_l = BeautifulSoup(res_l.text, 'lxml').select_one('ol.article-list').select('li')
    if len(soup_l) == 0:   ##若讀不到html成text則跳出迴圈
        print "queue latest done"        
        break    
    else:
        queue.put(page_url_l)
        continue
        
#今日熱門
c = 2   ##此不能更改
d = 700 ##設定最大值為700頁
URL = "https://www.pixnet.net/blog/articles/category/29/hot/{}"
for page_h in range(c, d):    
    page_url_h=URL.format(page_h)
    res_h = r.get(page_url_h)
    soup_h = BeautifulSoup(res_h.text, 'lxml').select_one('ol.article-list').select('li')      
    if len(soup_h) == 0:   ##若讀不到html成text則跳出迴圈
        print "queue hot done"        
        break    
    else:
        queue.put(page_url_h)        
        continue
        
###   爬蟲實施抓取網頁
def worker():    
    while not queue.empty():
        global url
        url=queue.get()
        crawler(url) 
        
###   爬蟲程序   
    
def crawler(url): 
    res = r.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'lxml')
    aboxs = soup.select_one('ol.article-list').select('li')
    

    for abox in aboxs:
        
        ###  檢查url 是否重複
        load_url_3 = abox.select_one('h3').select_one('a')['href']
        if load_url_3 in pixnet_database_list:
            continue
            #print "this url has loaded"        
        else:
            try:
                dict3 = {}
                dict3['title'] =abox.select_one('h3').select_one('a').text
                dict3['url'] = abox.select_one('h3').select_one('a')['href']
                dict3['author'] = abox.select_one('span.meta').select_one('a').text
                dict3['date'] = abox.select_one('span.meta').text.strip().encode('utf-8').split('於')[1].split(' ')[1]
                dict3['reply'] = abox.select_one('span.meta').text.encode('utf-8').split("留言")[1].strip().split('(')[1].split(')')[0]
                box_list.append(dict3)
                pixnet_database_list.append(load_url_3)
                #print "done" #####測試有無執行到
            except Exception as e: 
                print "crawler(url) err"    
    

### 計時開始    
#s1 = datetime.now() 

####   啟動THREAD
threads = map(lambda i: Thread(target=worker), xrange(3))
map(lambda th: th.start(), threads)
map(lambda th: th.join(), threads)


#s2 = datetime.now() ####### 結束時間
#print "All  Finish "+str(s2-s1)+"!!" ####### 總共爬取資料耗費時間



##########   新增 url到比對資料庫

pixnet_database = json.dumps(pixnet_database_list, ensure_ascii=False)
with open('pixnet_url_database.json', 'w') as a:
    a.write(pixnet_database.encode('utf-8'))            
    a.close() 


##########    存檔

time = time.strftime("%Y%m%d")
traveljson = json.dumps(box_list, ensure_ascii=False)
with open('pixnet_latest_hot_{}.json'.format(time), 'w') as a:
    a.write(traveljson.encode('utf-8'))
    print 'case close'
    

### 計時結束     
#s2 = datetime.now() 
#print "All  Finish "+str(s2-s1)+"!!" ####### 總共爬取資料耗費時間
    
print "catch " + str(len(box_list)) + " latest+hot urls"


    
    
    
    


# In[ ]:



