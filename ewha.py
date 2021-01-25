from bs4 import BeautifulSoup
from selenium import webdriver
import time
driver = webdriver.Chrome(r'C:\Users\HongheeLee\chromedriver')

# URL 설정 및 브라우저 실행
keyword = '쇼코의+미소+최은영'
url_ewha = "http://lib.ewha.ac.kr/search/tot/result?st=KWRD&si=TOTAL&websysdiv=tot&q=" + keyword
driver.get(url_ewha)

# 대출현황 보기 위해 토글 열기
# 유독 이대 도서관 홈페이지에서 클릭이 불규칙적임. 어떤 토글은 열릴 때도 있고 아닐 때도 있고, 잘못 클릭해서 다른 페이지로 넘어갈 때도 있고.
jss = driver.find_elements_by_xpath("//p[@class='location']/a/span")
for js in jss:
    js.click()
    time.sleep(0.5)

# 크롤링 토대
time.sleep(5)
req = driver.page_source
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
soup = BeautifulSoup(req, 'html.parser')
lis = soup.select("div.result > form > fieldset > ul > li")

ewha_list = []

# 도서 정보 가져오기
count = 0
for li in lis:
    ewha_dict = {}
    loc_list = []
    status_list =[]

    title = li.select_one("dl > dd.title > a").text.split("/")[0].strip()
    bookcover = li.select_one("dl > dd.book > a > img")['src']
    author = li.select_one("dl > dd.title > a").text.split("/")[1].strip()
    company = li.select_one("dl > dd.info").text.split(",")[0].split(":")[1].strip()
    year = li.select_one("dl > dd.info").text.split(",")[1].strip()
    book_url = li.select_one("dl > dd.book > a")['href']
    locs = li.select("dl > dd.holdingInfo > div > p.location > a")
    divs = li.select("dl > dd.holdingInfo > div > div.holdingW")

    for loc in locs:
        if loc:
            loc = loc.text
            loc_list.append(loc)

    for div in divs:
        status_dict = {}
        trs = div.select("div.listTable > table > tbody > tr")
        for tr in trs:
            book_loc = tr.select_one("td.location.expand").text
            callnum = tr.select_one("td.callNum").text
            borrow = tr.select_one("td > span").text
            status_dict['book_loc'] = book_loc
            status_dict['callnum'] = callnum
            status_dict['borrow'] = borrow
            status_list.append(status_dict)

    ewha_dict['title']=title
    ewha_dict['bookcover']=bookcover
    ewha_dict['author']=author
    ewha_dict['company']=company
    ewha_dict['year']=year
    ewha_dict['book_url'] = book_url
    ewha_dict['loc']=loc_list
    ewha_dict['status'] = status_list

    ewha_list.append(ewha_dict)

    count += 1
    if count == 2:
            break
print(ewha_list)
    
driver.close()