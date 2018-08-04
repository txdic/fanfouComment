import requests
import json
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
import random


url = 'http://www.douban.com/'

# 浏览器头部
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
        'Referer': 'http://www.douban.com/',
        'Host': 'www.douban.com',
        #'Cookie': 'appver=1.5.0.75771'
        'Cookie': 'appver=2.0.2'}
session=requests.Session()
resp=session.post(url,headers=headers)


# 下载书的评论
# 找到豆瓣特定页面，以及第几页，爬取书的相关信息。
def get_page_books(page):
    html = session.get('https://book.douban.com/tag/哲学?start={}'.format(page))
    soup = BeautifulSoup(html.text,"lxml")
    books_info = soup.find_all("li", {"class": "subject-item"})
    
    people = [info.find_all("span", {"class": "pl"})[0].text.strip() for info in books_info]
    rates = [rate.find_all("span", {"class": "rating_nums"}) for rate in books_info]
    
    
    book_link = [book.h2.a['href'] for book in books_info]
    book_id = [re.findall('subject/(\d+)/',link)[0] for link in book_link]
    book_name = [book.h2.a.text.replace(' ','').replace('\n','') for book in books_info]
    book_rate = [float(rate[0].text) if len(rate) > 0 else 0 for rate in rates]
    book_pic = [pic.img['src'] for pic in books_info]
    book_people = [int(re.findall('(\d+)人评价',pl)[0]) if len(pl) > 0 else 0 for pl in people]
    return (book_name, book_id,book_rate,book_link,book_pic,book_people)

# 根据书的信息，进入书的页面，得到该书的评论的json数据。
def comment_data(book_id):
    r = session.get('https://api.douban.com/v2/book/{}/comments'.format(book_id))
    data = json.loads(r.text)
    return data

# 根据json数据，得到该书的评论。
def get_comment(data,page_books_name,page_books_rate,page_books_link,
                page_books_pic,page_books_id,page_books_people,num):
    i=0
    flag=0
    book_commnets = []
    while flag==0:
        vote = int(data['comments'][i]['votes'])
        comment = data['comments'][i]['summary']
        name = data['comments'][i]['author']['name']
        information = (comment,vote,name,page_books_name[num],page_books_rate[num],
                       page_books_link[num],page_books_pic[num], page_books_id[num],
                      page_books_people[num])
        #print(information)
        
        if vote < 100:
            flag = 1
            if i == 0:
                book_commnets.append(information)         
        else: book_commnets.append(information)

        i=i+1
    return book_commnets

# 把书的信息进行整合。
def get_comments_list(comments_list, book_info):
        
    page_books_name = book_info[0]
    page_books_id = book_info[1]    
    page_books_rate = book_info[2]
    page_books_link = book_info[3]
    page_books_pic = book_info[4]
    page_books_people = book_info[5]
    
    for num, book_id in enumerate(page_books_id):
        print(num, page_books_name[num])
        try:
            data = comment_data(book_id)
            print(data.keys())
            time.sleep(5)
            book_commnets = get_comment(data,page_books_name,page_books_rate,
                                        page_books_link,page_books_pic,page_books_id,
                                        page_books_people,num)
            
            for info in book_commnets:
                comments_list.append(info)
        except:
            print('there is an error!')
            continue
        #if num == 4: break
    
    return comments_list

# 开始爬取网页信息
comments_list = []
for page in range(200,260,20):
    print('this is page {}'.format(int(page/20+1)))
    book_info = get_page_books(page)
    #print(book_info)
    comments_list = get_comments_list(comments_list, book_info)
    

df = pd.DataFrame(comments_list, columns = ['commnet','vote','nick','name','rate','link','pic','id','people'])
#df_db = pd.read_excel('douban_1.xlsx')
#df_2 = pd.concat([df_db,df])
df.to_excel('douban_book.xlsx')
print('ok!')