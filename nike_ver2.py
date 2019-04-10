#-*-encoding:utf8:-*-
''' --------------------------------- INPUT YOUR CONFIG --------------------------------- '''
MONITOR_DELAY = 30 # second, if your input 10, monitor interval 10 second
PAGE_DELAY = 4 # Page to Page Delay second
discord_webhook = 'YOUR_WEBHOOK'
startPage = 1
endPage = 5 # example 1 ~ 5 -> include(1,2,3,4,5)

''' ------------------------------------------------------------------------------------- '''
import requests
from bs4 import BeautifulSoup
import time
import random
from log import *
from discord_hooks import Webhook

def send_embed(alert_type,product):
    '''
    (str, str, list, str, str, str) -> None
    Sends a discord alert based on info provided.
    '''
    # Set webhook
    url = discord_webhook

    # Create embed to send to webhook
    embed = Webhook(url, color=123123)

    # Set author info
    embed.set_author(name='Nike', icon='https://static-breeze.nike.co.kr/kr/ko_kr/cmsstatic/theme/52/android-icon-36x36.png')

    # Set product details
    if(alert_type == "RESTOCK"):
        embed.set_desc("RESTOCK: " + "title")
    elif(alert_type == "NEW"):
        embed.set_desc("NEW: " + product.title)
    # Name, Code, Color, Date, Price
    # Early Link
    # Time
    embed.add_field(name="Name", value=product.name)
    embed.add_field(name="Code", value=product.code)
    embed.add_field(name="Color", value=product.color)
    embed.add_field(name="Price", value=product.price)
    embed.add_field(name="Link", value=product.siteLink)
    embed.add_field(name="Time", value=product.pTime)
    embed.add_field(name="ImgLink", value=product.imgLink)


    # Set product image
    embed.set_thumbnail(product.imgLink)
    embed.set_image(product.imgLink)

    # Set footer
    embed.set_footer(text='Nike by @DevHong', icon='https://static-breeze.nike.co.kr/kr/ko_kr/cmsstatic/theme/52/android-icon-36x36.png', ts=True)
    # Send Discord alert
    embed.post()
class Product:
    def __init__(self, title,name, code,color, price, imgLink, siteLink,pTime):
        self.title = title
        self.name = name
        self.code = code
        self.color = color
        self.price = price
        self.siteLink = siteLink
        self.imgLink = imgLink
        self.pTime = pTime

def read_from_txt(path):
    '''
    (None) -> list of str
    Loads up all sites from the sitelist.txt file in the root directory.
    Returns the sites as a list
    '''
    # Initialize variables
    raw_lines = []
    lines = []

    # Load data from the txt file
    try:
        f = open(path, "r")
        raw_lines = f.readlines()
        f.close()

    # Raise an error if the file couldn't be found
    except:
        log('e', "Couldn't locate <" + path + ">.")

    if(len(raw_lines) == 0):
        pass
    # Parse the data
    for line in raw_lines:
        lines.append(line.strip("\n"))

    # Return the data
    return lines

def get_proxy(proxy_list):
    '''
    (list) -> dict
    Given a proxy list <proxy_list>, a proxy is selected and returned.
    '''
    # Choose a random proxy
    proxy = random.choice(proxy_list)

    # Set up the proxy to be used
    proxies = {
        "http": str(proxy),
        "https": str(proxy)
    }

    # Return the proxy
    return proxies

def get_now_time():
    """
    :return: now time stamp
    """
    now = time.localtime()
    return "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

def get_bs_by_url(_url):
    """
    :param _url: target URL
    :return: bs4 object
    """
    return BeautifulSoup(requests.get(_url,timeout=5).text,'lxml')

def build_db():
    baseUrl = "https://www.nike.com"
    url = "https://www.nike.com/kr/ko_kr/w/men/fw?page={}&pageSize=40&lineSize=5&_={}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
    }
    proxies = get_proxy(proxy_list)
    for pageIdx in range(startPage,endPage+1):
        ts = int(time.time() * 1000)
        now = time.localtime()
        pTime = "%04d-%02d-%02d %02d:%02d:%02d" % (
        now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        link = url.format(pageIdx, ts)
        log('i',"{} page build ...".format(pageIdx))
        try:
            r = requests.get(link, timeout=5, verify=False,headers=headers)
        except:
            log('e', "Connection to URL <" + link + "> failed. Retrying...")
            try:
                if (use_proxies):
                    proxies = get_proxy(proxy_list)
                    r = requests.get(link, proxies=proxies, timeout=8, verify=False,headers=headers)
                else:
                    r = requests.get(link, timeout=8, verify=False,headers=headers)
            except:
                log('e', "Connection to URL <" + link + "> failed.")
        bs = BeautifulSoup(r.text, 'lxml')
        ul = bs.find('ul', class_='uk-grid item-list-wrap')
        lis = ul.find_all('li')
        if len(lis) == 0:
            break
        for li in lis:
            try:
                pId = str(li.find('input', {"name": "productId"})['value'])
                pUrl = baseUrl + li.find('input', {"name": "producturl"})['value']
                iUrl = li.find('img')['src']
                name = li.find('span', class_='item-title').get_text().strip()
                itemLocation = li.find('div', class_='item-location').get_text().strip()
                price = li.find('span', class_='item-price').get_text().strip()
                color = "COLOR"
                code = "CODE"
                # color, code = get_detail(pUrl)
                #print(strFormat.format(itemLocation, name, code, pId, color, price, iUrl, iUrl,pTime))
                products_list[pId] = Product(itemLocation,name,code,color, price, iUrl, pUrl,pTime)
            except:
                pass
        time.sleep(PAGE_DELAY)
def get_detail(_url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
    }
    html = requests.get(_url, headers=headers)
    bs = BeautifulSoup(html.text, 'lxml')
    color =bs.find('span',class_='style-color').get_text().split(":",maxsplit=2)[1].strip()
    code = bs.find('span',class_='style-code')['data-model']
    return color,code
def monitor():
    baseUrl = "https://www.nike.com"
    url = "https://www.nike.com/kr/ko_kr/w/men/fw?page={}&pageSize=40&lineSize=5&_={}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
    }
    proxies = get_proxy(proxy_list)
    log('i', "Checking atmos products...")
    print("[Monitor] ",end='',flush=True)
    for pageIdx in range(startPage, endPage + 1):
        ts = int(time.time() * 1000)
        now = time.localtime()
        pTime = "%04d-%02d-%02d %02d:%02d:%02d" % (
        now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        link = url.format(pageIdx, ts)
        print("{}p".format(pageIdx),end=',',flush=True)
        try:
            r = requests.get(link, timeout=5, verify=False,headers=headers)
        except:
            log('e', "Connection to URL <" + link + "> failed. Retrying...")
            try:
                if (use_proxies):
                    proxies = get_proxy(proxy_list)
                    r = requests.get(link, proxies=proxies, timeout=8, verify=False,headers=headers)
                else:
                    r = requests.get(link, timeout=8, verify=False,headers=headers)
            except:
                log('e', "Connection to URL <" + link + "> failed.")
        try:
            bs = BeautifulSoup(r.text, 'lxml')
            ul = bs.find('ul', class_='uk-grid item-list-wrap')
            lis = ul.find_all('li')
            if len(lis) == 0:
                break
            for li in lis:
                try:
                    pId = str(li.find('input', {"name": "productId"})['value'])
                    pUrl = baseUrl + li.find('input', {"name": "producturl"})['value']
                    iUrl = li.find('img')['src']
                    name = li.find('span', class_='item-title').get_text().strip()
                    itemLocation = li.find('div', class_='item-location').get_text().strip()
                    price = li.find('span', class_='item-price').get_text().strip()
                    color = "COLOR"
                    code = "CODE"
                    try:
                        products_list[pId]
                    except:
                        color, code = get_detail(pUrl)
                        log('s', "Added " + name + " to the database.")
                        products_list[pId] = Product(itemLocation,name,code,color, price, iUrl, pUrl,pTime)
                        send_embed('NEW', products_list[pId])
                except:
                    pass
            time.sleep(PAGE_DELAY)
        except:
            f = open("error.log","w",encoding='utf8')
            f.write(r.text)
            f.close()
            pass
    print('',flush=True)

''' --------------------------------- RUN --------------------------------- '''
if __name__ == "__main__":
    # Ignore insecure messages
    requests.packages.urllib3.disable_warnings()

    # Load proxies (if available)
    proxy_list = read_from_txt("proxies.txt")
    log('i', "Loaded " + str(len(proxy_list)) + " proxies.")
    if (len(proxy_list) == 0):
        use_proxies = False
    else:
        use_proxies = True

    # Initialize variables
    proxies = get_proxy(proxy_list)


    # Build database
    products_list = {}
    build_db()

    log('i',"총 {}개 상품 Build".format(len(products_list.keys() )))
    # Monitor products
    while (True):
        monitor()
        time.sleep(MONITOR_DELAY)