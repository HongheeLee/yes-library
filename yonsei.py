from bs4 import BeautifulSoup
from selenium import webdriver
driver = webdriver.Chrome(r'C:\Users\HongheeLee\chromedriver')
import time

# URL 설정 및 실행
keyword = '쇼코의+미소+최은영'
url_yonsei = "https://library.yonsei.ac.kr/main/searchBrief?q=" + keyword
driver.get(url_yonsei)

# 대출 현황 보기 위해 토글 열기
campus = list(driver.find_elements_by_xpath("//a[@class='availableBtn']"))
for i in range(len(campus)):
    campus[i].click()
    locs = list(driver.find_elements_by_xpath("//div[@class='locationList']"))
    locs[i].click()
        
# 크롤링 토대
time.sleep(3)
req = driver.page_source
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
soup = BeautifulSoup(req, 'html.parser')
divs = soup.select("#divContent > div.searchResult > div.pcWrap > div.mid > div > div.sectionList > div")

api = {'libraryStatus': 
    {
    'result':'success',
    'msg' : '정상 처리되었습니다.',
    'sogang': [],
    'yonsei': [],
    'ewha' : []
    }
    }
yonsei_list = []

# 도서 정보 가져오기
count1 = 0
for div in divs:
    yonsei_dict = {}
    loc_list = []
    status_list = []

    title = div.select_one("dl > dt > a").text
    bookcover = div.select_one("dd.imgList > a > span > img")['src']
    author = div.select_one("dd.imgList > ul > li:nth-child(1)").text
    company = div.select_one("dd.imgList > ul > li:nth-child(2)").text
    year = div.select_one("dd.imgList > ul > li:nth-child(3)").text
    book_url = div.select_one("dl > dt > a")['href']
    locs = div.select("a.availableBtn")
    docs = div.select("div.locationList")

    # 대출 현황 표 가져오기
    for loc in locs:
        location = loc.parent.text
        loc_list.append(location)
        lis = loc.parent.parent.select("div > dl > dd > ul > li")
        for li in lis:
            status_dict = {}
            book_loc = li.parent.parent.parent.select_one("dt").text
            callnum = li.select_one("p:nth-child(1) > a").text
            borrow = li.select_one("p:nth-child(2) > a > span").text
            status_dict['book_loc'] = book_loc
            status_dict['callnum'] = callnum
            status_dict['borrow'] = borrow
            status_list.append(status_dict)
        
    yonsei_dict['title']=title
    yonsei_dict['bookcover']=bookcover
    yonsei_dict['author']=author
    yonsei_dict['company']=company
    yonsei_dict['year']=year
    yonsei_dict['book_url'] = book_url
    yonsei_dict['loc'] = loc_list
    yonsei_dict['status'] = status_list

    yonsei_list.append(yonsei_dict)

    count1 += 1
    if count1 == 2:
        break
api['libraryStatus']['yonsei'] = yonsei_list
api['libraryStatus']['url_yonsei'] = url_yonsei
print(api)

driver.close()

