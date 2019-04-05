import time
import requests
from bs4 import BeautifulSoup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
}

def get_detail(_url):
    html = requests.get(_url, headers=headers)
    bs = BeautifulSoup(html.text, 'lxml')
    color =bs.find('span',class_='style-color').get_text().split(":",maxsplit=2)[1].strip()
    code = bs.find('span',class_='style-code')['data-model']
    return color,code

strFormat ="""\
title: {}
Name : {}
Code : {}
pId  : {}
Color: {}
Price: {}
Link : {}
imgLink : {}
Time : {}
"""
baseUrl = "https://www.nike.com"
url = "https://www.nike.com/kr/ko_kr/w/men/fw?page={}&pageSize=40&lineSize=5&_={}"
pageIdx = 1
while True:
    ts = int(time.time()*1000)
    now = time.localtime()
    pTime = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    html = requests.get(url.format(pageIdx,ts),headers=headers)
    pageIdx += 1
    bs = BeautifulSoup(html.text,'lxml')
    ul = bs.find('ul',class_='uk-grid item-list-wrap')
    lis = ul.find_all('li')
    if len(lis) == 0:
        print("끝")
        exit(-1)
    for li in lis[:1]:
        try:
            pId = li.find('input',{"name" : "productId"})['value']
            pUrl = baseUrl+li.find('input', {"name": "producturl"})['value']
            iUrl = li.find('img')['src']
            name = li.find('span',class_='item-title').get_text().strip()
            itemLocation = li.find('div',class_='item-location').get_text().strip()
            price = li.find('span',class_='item-price').get_text().strip()
            color = "COLOR"
            code = "CODE"
            #color, code = get_detail(pUrl)
            print(strFormat.format(itemLocation,name,code,pId,color,price,pUrl,iUrl,pTime))
        except:
            pass



