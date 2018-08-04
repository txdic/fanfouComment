import requests
import json
import pandas as pd

# 浏览器头部
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
        'Referer': 'http://music.163.com/',
        'Host': 'music.163.com',
        #'Cookie': 'appver=1.5.0.75771'
        'Cookie': 'appver=2.0.2'
        }

# 根据歌手姓名，得到歌手在网易云音乐的ID
def get_artist_id(name):
    url = 'http://music.163.com/api/search/pc'
  
    parameter = {'s': name, 'sub': 'False', 'type': '100', 'offset': '0', 'limit':'1'}
    response = requests.post(url=url, headers=headers, data=parameter)

    infomation = json.loads(response.text)
    artist_id = infomation['result']['artists'][0]['id']
    
    return artist_id

# 根据歌手ID，得到该歌手在网易云音乐所有专辑信息
def get_albums(artist_id):
    
    url = 'http://music.163.com/api/artist/albums/{}?offset={}&limit={}'.format(artist_id,0,150)
    
    response = requests.get(url=url, headers=headers)
    
    infomation = json.loads(response.text)
    infomation = infomation['hotAlbums']
    albums = []
    for item in infomation:
        album_name = item['name']
        album_id = item['id']
        album_pic1 = item['blurPicUrl']
        album_pic2 = item['picUrl']
        albums.append((album_name,album_id,album_pic1,album_pic2))
    
    return albums

# 根据专辑信息，得到专辑图片
def album_pics(albums):
    albums_pics = {}
    for album in albums:
        albums_pics[album[0]] = (album[2],album[3])
    
    return albums_pics

# 得到歌曲的信息
def get_songs(albums):
    albums_songs = {}
    for album in albums:
        url = 'http://music.163.com/api/album/{}/'.format(album[1])
        response = requests.get(url=url, headers=headers)
        infomation = json.loads(response.text)    
        infomation = infomation['album']['songs']
        
        songs = []
        for item in infomation:
            song_name = item['name']
            song_id = item['id']
            songs.append((song_name,song_id))
        
        albums_songs[album[0]] = songs
        
    return albums_songs

# 根据歌曲信息，得到该歌曲所有的精彩评论。
def getcomments(musicid):
    url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_{}?csrf_token=5594eaee83614ea8ca9017d85cd9d1b3'.format(musicid)
    payload = {
        'params': '4hmFbT9ZucQPTM8ly/UA60NYH1tpyzhHOx04qzjEh3hU1597xh7pBOjRILfbjNZHqzzGby5ExblBpOdDLJxOAk4hBVy5/XNwobA+JTFPiumSmVYBRFpizkWHgCGO+OWiuaNPVlmr9m8UI7tJv0+NJoLUy0D6jd+DnIgcVJlIQDmkvfHbQr/i9Sy+SNSt6Ltq',
        'encSecKey': 'a2c2e57baee7ca16598c9d027494f40fbd228f0288d48b304feec0c52497511e191f42dfc3e9040b9bb40a9857fa3f963c6a410b8a2a24eea02e66f3133fcb8dbfcb1d9a5d7ff1680c310a32f05db83ec920e64692a7803b2b5d7f99b14abf33cfa7edc3e57b1379648d25b3e4a9cab62c1b3a68a4d015abedcd1bb7e868b676'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
        'Referer': 'http://music.163.com/song?id={}'.format(musicid),
        'Host': 'music.163.com',
        'Origin': 'http://music.163.com'
    }

    response = requests.post(url=url, headers=headers, data=payload)
    data = json.loads(response.text)
    hotest_comments = []
    for hotcomment in data['hotComments']:
        if int(hotcomment['likedCount'])>10000:
            item = {
                'nickname': hotcomment['user']['nickname'],
                'content': hotcomment['content'],
                'likedCount': hotcomment['likedCount']
            }
            hotest_comments.append(item)
    
    if len(hotest_comments)==0:        
        if len(data['hotComments']) > 0:
            hotcomment = data['hotComments'][0]
            item = {
                'nickname': hotcomment['user']['nickname'],
                'content': hotcomment['content'],
                'likedCount': hotcomment['likedCount']
            }
            hotest_comments.append(item)
        
        else: pass
                
    return hotest_comments

# 把歌曲和评论组合起来
def get_songs_comments(songs):
    comments = {}
    count=0
    for album in songs.keys():
        count=count+1
        song_commnets = []
        for song in songs[album]:
            musicid = song[1]
            comment = getcomments(musicid)
            song_commnets.append((song[0], comment))         
        comments[album] = song_commnets
        print('Album No.{}'.format(count))
    
    return comments

# 形成信息表
def df_input(raw, name, artist_id,albums_pics):
    artist_name = name
    artist_id = artist_id
    
    comment_list = []
    
    for album,album_value in raw.items():
        for song in album_value:
            song_name = song[0]
            song_value = song[1]
            for item in song_value:
                # 特别注意：item在song_value里就是就是一个字典
                # 参见函数：getcomments 
                item['artist'] = artist_name
                item['artist_id'] = artist_id
                item['album'] = album
                item['pic1'] = albums_pics[album][0]
                item['pic2'] = albums_pics[album][1]
                item['song'] = song_name
                comment_list.append(item)    
            
    return comment_list 

# 可在列表里任意增加歌手名字。
names = ['莫文蔚']
df_names = pd.DataFrame(columns=['album', 'artist', 'artist_id', 'content',
                                 'likedCount','nickname','pic1','pic2','song'])

# 把上述函数组装成主程序
for name in names:
    print(name)
    try:
        artist_id = get_artist_id(name)
        albums = get_albums(artist_id)
        
        albums_pics = album_pics(albums)
        songs = get_songs(albums)
        
        comments = get_songs_comments(songs)
        comment_list = df_input(comments, name, artist_id, albums_pics)
        df = pd.DataFrame(comment_list)
        df_names = pd.concat([df_names,df], sort=False)
    except: pass

df_names.to_excel('comments.xlsx')
print('ok!')