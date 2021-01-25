from bs4 import BeautifulSoup
from selenium import webdriver
import time

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
# 혹은 options.add_argument("--disable-gpu")

driver = webdriver.Chrome(r'C:\Users\HongheeLee\chromedriver', chrome_options=options)

# URL 설정 및 브라우저 실행
keyword = '쇼코의+미소+최은영'
url_sogang = "https://library.sogang.ac.kr/searchTotal/result?st=KWRD&si=TOTAL&q=" + keyword
driver.get(url_sogang)

    # 대출현황 보기 위해 토글 열기
jss = driver.find_elements_by_xpath("//p[@class='location']")
for js in jss:
    js.click()
    time.sleep(1)

# 크롤링 토대
time.sleep(5)
req = driver.page_source
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
soup = BeautifulSoup(req, 'html.parser')
lis = soup.select("#catalogs > ul > li")
sogang_list = []

api = {'libraryStatus': 
    {
    'result':'success',
    'msg' : '정상 처리되었습니다.',
    'sogang': [],
    'yonsei': [],
    'ewha' : [],
    }
}

# 도서 정보 가져오기
count = 0
for li in lis:
    sogang_dict = {}
    status_list = []

    title = li.select_one("p > a").text
    bookcover = li.select_one("div.information > p.bookCover > img")['src']
    author = li.select_one("div.information > p:nth-child(2)").text
    company = li.select_one("div.information > p:nth-child(3)").text
    year = li.select_one("div.information > p:nth-child(4)").text
    book_url = li.select_one("p > a")['href']
    loc = li.select_one("div.holdingInfo > div > p > a").text
    trs = li.select("div.holdingInfo > div > div > div > table > tbody > tr")
    
    for tr in trs:
        status_dict = {}
        order = tr.select_one("td.num.footable-first-column").text
        book_loc = tr.select_one("td.location").text
        callnum = tr.select_one("td.callNum").text
        borrow = tr.select_one("td.bookStatus").text
        return_date = tr.select_one("td.returnDate.footable-last-column").text

        status_dict['book_loc'] = book_loc
        status_dict['callnum'] = callnum
        status_dict['borrow'] = borrow
        status_list.append(status_dict)
    
    sogang_dict['title']=title
    sogang_dict['bookcover']=bookcover
    sogang_dict['author']=author
    sogang_dict['company']=company
    sogang_dict['year']=year
    sogang_dict['book_url'] = book_url
    sogang_dict['loc']=loc
    sogang_dict['status'] = status_list

    sogang_list.append(sogang_dict)
    
    # 원하는 권수만큼 크롤링하고 반복문 종료.
    count += 1
    if count == 2:
        break

api['libraryStatus']['sogang']= sogang_list
api['libraryStatus']['url_sogang'] = url_sogang
print(api)


driver.close()