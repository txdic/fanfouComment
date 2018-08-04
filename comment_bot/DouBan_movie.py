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


# 下载电影的评论

# 找到豆瓣特定页面，以及第几页，爬取电影的相关信息。
def get_page_movies(page):
    html = session.get('https://movie.douban.com/tag/喜剧?start={}'.format(page))
    soup = BeautifulSoup(html.text,"lxml")
    movies_info = soup.find_all("table", {"class": "",'width':'100%'})
    #pictures = soup.find_all("div", {"class": "pic"})
    rates = [movie.find_all("span", {"class": "rating_nums"}) for movie in movies_info]
    
    movie_link = [movie.a['href'] for movie in movies_info]
    movie_id = [re.findall('subject/(\d+)/',link)[0] for link in movie_link]
    movie_name = [movie.find_all("a", {"class": ""})[0].text.split()[0].strip() for movie in movies_info]
    movie_rate = [rate[0].text if len(rate)>0 else 0 for rate in rates]
    movie_pic = [pic.img['src'] for pic in movies_info]
    
    return (movie_name, movie_id, movie_rate, movie_link, movie_pic)

# 根据电影的信息，进入电影的页面，得到该电影的评论。
def comment_data(movie_id):
    r = session.get('https://movie.douban.com/subject/{}/comments'.format(movie_id))
    soup = BeautifulSoup(r.text,"lxml")
    comemnts = [comment.text for comment in soup.find_all('span',{'class':'short'})]
    rates = [int(rate.text) for rate in soup.find_all('span',{'class':'votes'})]
    nicks = [nick.a.text for nick in soup.find_all('span', {'class':"comment-info"})]
    
    hotest_comments = []
    
    for item in zip(comemnts,rates,nicks):
        if item[1] > 500:
            hotest_comments.append(item)
    if len(hotest_comments) == 0:
        hotest_comments.append(next(zip(comemnts,rates,nicks)))
    
    return hotest_comments

# 把评论信息和该电影的其他信息一起整合起来
def get_comments_list(comments_list, movie_info):
        
    page_movies_name = movie_info[0]
    page_movies_id = movie_info[1]    
    page_movies_rate = movie_info[2]
    page_movies_link = movie_info[3]
    page_movies_pic = movie_info[4]
    
    for num, movie_id in enumerate(page_movies_id):
        print(num, page_movies_name[num])
        try:
            data = comment_data(movie_id)
            movie_detail = (page_movies_name[num], page_movies_rate[num], page_movies_link[num], 
                            page_movies_pic[num], page_movies_id[num])
            comments = [comment + movie_detail for comment in data]
            
            time.sleep(5)
            
            for info in comments:
                comments_list.append(info)
        except:
            print('there is an error!')
            continue
        #if num == 4: break
    
    return comments_list

# 开始爬取。
comments_list = []
for page in range(140,180,20):
    print('this is page {}'.format(int(page/20+1)))
    movie_info = get_page_movies(page)
    print(movie_info)
    comments_list = get_comments_list(comments_list, movie_info)
    

df_movie = pd.DataFrame(comments_list,columns = ['commnet','vote','nick','name','rate','link','pic','id'])

df_movie.to_excel('douban_movie.xlsx')
print('ok!')