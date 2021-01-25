from flask import Flask, render_template, jsonify, request
app = Flask(__name__)
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from pymongo import MongoClient
from multiprocessing import Process, Manager
import json

client = MongoClient('mongodb://ID, PW)
db = client.dbsparta

# 로컬 환경에서 chromedriver 실행
# driver = webdriver.Chrome(r'C:\Users\HongheeLee\chromedriver')

from selenium.webdriver.chrome.options import Options
# AWS EC2 서버에서 headless로 chromebrowser 실행
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

# driver = webdriver.Chrome(options=chrome_options, executable_path="/home/ubuntu/chromedriver")

def sogang_search(keyword, api):
    driver1 = webdriver.Chrome(options=chrome_options, executable_path="/home/ubuntu/chromedriver")
    url_sogang = "https://library.sogang.ac.kr/searchTotal/result?st=KWRD&si=TOTAL&q=" + keyword
    driver1.get(url_sogang)
    time.sleep(0.5)
     # 대출현황 보기 위해 토글 열기
    jss = driver1.find_elements_by_xpath("//p[@class='location']/a")
    js_count = 0
    for js in jss:
        js.click()
        time.sleep(0.3)
        js_count += 1
        if js_count == 2:
            break

    # 크롤링 토대
    req = driver1.page_source
    soup = BeautifulSoup(req, 'html.parser')
    lis = soup.select("#catalogs > ul > li")
    sogang_list = []
    count = 0

    for li in lis:
        sogang_dict = {}
        status_list = []
        loc_list = []
        # 가져와야 할 도서 정보 경로 지정
        title = li.select_one("p > a")
        if title is None:
            break
        else:
            title = title.text
        bookcover = li.select_one("div.information > p.bookCover > img")['src']
        author = li.select_one("div.information > p:nth-child(2)").text

        company = li.select_one("div.information > p:nth-child(3)").text
        year = li.select_one("div.information > p:nth-child(4)").text
        book_url = "https://library.sogang.ac.kr/" +li.select_one("p > a")['href']
        loc = li.select_one("div.holdingInfo > div > p > a").text
        loc_list.append(loc)
        trs = li.select("div.holdingInfo > div > div > div > table > tbody > tr")
        
        # 표 안에 있는 정보들은 한번 더 타고 들어가야 함.
        for tr in trs:
            status_dict = {}
            book_loc = tr.select_one("td.location").text
            callnum = tr.select_one("td.callNum").text
            borrow = tr.select_one("td.bookStatus").text

            status_dict['book_loc'] = book_loc
            status_dict['callnum'] = callnum
            status_dict['borrow'] = borrow
            status_list.append(status_dict)
        
        # dict에 추가
        sogang_dict['title']=title
        if (bookcover[0] != '/'):
            sogang_dict['bookcover']=bookcover
        else:
            sogang_dict['bookcover'] = []
        sogang_dict['author']=author
        sogang_dict['company']=company
        sogang_dict['year']=year
        sogang_dict['book_url'] = book_url
        sogang_dict['loc']=loc_list
        sogang_dict['status'] = status_list

        sogang_list.append(sogang_dict)
        
        # 원하는 권수만큼 크롤링하고 반복문 종료.
        count += 1
        if count == 2:
            break

    # api에 추가
    api['sogang']= sogang_list
    driver1.quit()

def yonsei_search(keyword, api):
    driver2 = webdriver.Chrome(options=chrome_options, executable_path="/home/ubuntu/chromedriver")
    url_yonsei = "https://library.yonsei.ac.kr/main/searchBrief?q=" + keyword
    driver2.get(url_yonsei)
    time.sleep(0.5)
    
    # 대출 현황 보기 위해 토글 열기
    campus = list(driver2.find_elements_by_xpath("//a[@class='availableBtn']"))
    for i in range(len(campus)):
        campus[i].click()
        locs = list(driver2.find_elements_by_xpath("//div[@class='locationList']"))
        locs[i].click()

    # 크롤링 토대
    req = driver2.page_source
    soup = BeautifulSoup(req, 'html.parser')
    divs = soup.select("div.bookSection > div.sectionList > .divList")
    yonsei_list = []

    # 가져와야 할 도서 정보 경로 지정
    count1 = 0
    for div in divs:
        yonsei_dict = {}
        loc_list = []
        status_list = []

        title = div.select_one("dl > dt > a")
        if title is None:
            break
        else:
            title = title.text
        bookcover = div.select_one("dl > dd.imgList > a > span > img")['src']
        author = div.select_one("dd.imgList > ul > li:nth-child(1)").text
        company = div.select_one("dd.imgList > ul > li:nth-child(2)").text
        year = div.select_one("dd.imgList > ul > li:nth-child(3)").text
        book_url = "https://library.yonsei.ac.kr/" + div.select_one("dl > dt > a")['href']
        locs = div.select("a.availableBtn")
        docs = div.select("div.locationList")

        # 표 안에 있는 정보들은 한번 더 타고 들어가야 함.
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

        # dict에 추가     
        yonsei_dict['title']=title
        if (bookcover[0] != '/'):
            yonsei_dict['bookcover']=bookcover
        else:
            yonsei_dict['bookcover'] = []
        yonsei_dict['author']=author
        yonsei_dict['company']=company
        yonsei_dict['year']=year
        yonsei_dict['book_url'] = book_url
        yonsei_dict['loc'] = loc_list
        yonsei_dict['status'] = status_list

        yonsei_list.append(yonsei_dict)
        
        # 원하는 권수만큼 크롤링하고 반복문 종료.
        count1 += 1
        if count1 == 2:
            break

    # api에 추가       
    api['yonsei'] = yonsei_list
    driver2.quit()

def ewha_search(keyword, api):
    driver3 = webdriver.Chrome(options=chrome_options, executable_path="/home/ubuntu/chromedriver")
    url_ewha = "http://lib.ewha.ac.kr/search/tot/result?st=KWRD&si=TOTAL&websysdiv=tot&q=" + keyword
    driver3.get(url_ewha)
    time.sleep(1)
    # 대출현황 보기 위해 토글 열기
    jss = driver3.find_elements_by_xpath("//p[@class='location']/a/span")
    js_count = 0
    for js in jss:
        js.click()
        time.sleep(0.5)
        js_count += 1
        if js_count == 2:
            break

    # 크롤링 토대
    req = driver3.page_source
    soup = BeautifulSoup(req, 'html.parser')
    lis = soup.select("div.result > form > fieldset > ul > li")
    ewha_list = []

    # 가져와야 할 도서 정보 경로 지정
    count = 0
    for li in lis:
        ewha_dict = {}
        loc_list = []
        status_list =[]

        title = li.select_one("dl > dd.title > a")
        if title is None:
            break
        else:
            title = title.text.split("/")[0].strip()

        bookcover = li.select_one("dl > dd.book > a > img")['src']
        author = li.select_one("dl > dd.title > a").text.split("/")[1].strip()
        company = li.select_one("dl > dd.info").text.split(",")[0].split(":")[1].strip()
        year = li.select_one("dl > dd.info").text.split(",")[1].strip()
        book_url = "http://lib.ewha.ac.kr/" + li.select_one("dl > dd.book > a")['href']
        locs = li.select("dl > dd.holdingInfo > div > p.location > a")
        divs = li.select("dl > dd.holdingInfo > div > div.holdingW")

        for loc in locs:
            if loc:
                loc = loc.text
                loc_list.append(loc)

        # 표 안에 있는 정보들은 한번 더 타고 들어가야 함.
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

        # dict에 추가
        ewha_dict['title']=title
        if (bookcover[0] != '/'):
            ewha_dict['bookcover']=bookcover
        else:
            ewha_dict['bookcover'] = []
        ewha_dict['author']=author
        ewha_dict['company']=company
        ewha_dict['year']=year
        ewha_dict['book_url'] = book_url
        ewha_dict['loc']=loc_list
        ewha_dict['status'] = status_list

        ewha_list.append(ewha_dict)

        # 원하는 권수만큼 크롤링하고 반복문 종료.
        count += 1
        if count == 2:
                break
    # api에 추가
    api['ewha']= ewha_list
    driver3.quit()

def multi(keyword, api):
    p1 = Process(target=sogang_search, args=(keyword, api)) 
    p2 = Process(target=yonsei_search, args=(keyword, api)) 
    p3 = Process(target=ewha_search, args=(keyword, api)) 

    # start로 각 프로세스를 시작합니다. func1이 끝나지 않아도 func2가 실행됩니다.
    p1.start()
    p2.start()
    p3.start()

    # # join으로 각 프로세스가 종료되길 기다립니다 p1.join()이 끝난 후 p2.join()을 수행합니다
    p1.join()
    p2.join()
    p3.join()

## HTML을 주는 부분
@app.route('/')
def home():
   return render_template('main.html')

@app.route('/result')
def result():
    keyword = request.args.get('keyword_give')
    return render_template('result.html', keyword = keyword)

# API 역할을 하는 부분
@app.route('/keywords', methods=['POST'])
def get_keyword():
    keyword_receive = request.form['keyword_give']
    doc = {
        'keyword' : keyword_receive
    }
    db.search.insert_one(doc)
    return jsonify({'result':'success', 'msg': '검색 완료'})

@app.route('/keywords', methods=['GET'])
def put_keywords():
    keywords = list(db.search.find({},{'_id':False}))[-1:-5:-1]
    return jsonify({'result': 'success', 'keywords':keywords})

@app.route('/result/getlist', methods=['GET'])
def give_result():
    keyword_receive = request.args.get('keyword_give')
    with Manager() as manager:
        api = manager.dict()
        multi(keyword_receive, api)
        api = json.dumps(api.copy(), ensure_ascii = False)
        return jsonify({'result': "success", 'msg':'정상 처리되었습니다.', 'row':api})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)