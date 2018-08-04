import fanfou
import time
import random
import datetime
import pandas as pd

# API 协议 
consumer = {'key': '****** your  key ************', 
            'secret': '****** your  secret ************'} 
# 这里要替换成“需要发言”的 ID 和密码
client = fanfou.XAuth(consumer, '***your username***', '***your password***')

# 必要的一步绑定
fanfou.bound(client)

# 读取评论文件
df_ne = pd.read_excel('./data/netease_2.xlsx')
df_ne = df_ne.reset_index(drop=True)

df_db = pd.read_excel('./data/douban_book_1.xlsx').reset_index(drop=True)
df_db = df_db.drop(df_db[df_db.commnet.duplicated(keep='last')].index.values)

df_db_movie = pd.read_excel('./data/douban_movie_1.xlsx').reset_index(drop=True)
df_db_movie = df_db_movie.drop(df_db_movie[df_db_movie.commnet.duplicated(keep='last')].index.values)

# 网易云音乐的评论
def get_text_ne(df_ne):
    num = random.choice(df_ne.index)
    comment = df_ne.loc[num, 'content']
    song = df_ne.loc[num, 'song']
    nick = df_ne.loc[num, 'nickname']
    pic = df_ne.loc[num, 'pic1']
    vote = df_ne.loc[num, 'likedCount']
    if nick == '此账号涉嫌违规已被封禁' or nick == '帐号已注销':
        nick = '佚名'
    text = '{}——网易云音乐 {}| 评<{}>'.format(comment,nick,song)
    return text,pic,vote

# 豆瓣的评论
def get_text_db(df):
    num = random.choice(df.index)
    comment = df.loc[num, 'commnet']
    book = df.loc[num, 'name']
    nick = df.loc[num, 'nick']
    rate = df.loc[num, 'rate']
    pic = df.loc[num, 'pic']
    vote = df.loc[num, 'vote']
    if nick == '[已注销]':
        nick = '佚名'
    text = '{}——豆瓣{}分 {}| 评<{}>'.format(comment,rate, nick, book)
    return text,pic,rate,vote


df_text = pd.read_excel('mytext.xlsx')

while True:
    now = datetime.datetime.now()
    random_int = random.randint(1,3)
    # 当豆瓣评分不到7.6分，以及评论人数不足10位的时候，就舍掉。
    # 网易云音乐的评论人数门槛是要超过50人。
    try:
        if random_int == 1:
            text,pic,rate,vote = get_text_db(df_db)
            if float(rate) < 7.5 or int(vote) < 15: continue
                       
        elif random_int == 2:
            text,pic,vote = get_text_ne(df_ne)
            if vote < 300: continue
         
        else:
            text,pic,rate,vote = get_text_db(df_db_movie)
            if float(rate) < 7.5 or int(vote) < 15: continue
        
        #文本不能超过140个字   
        if len(text) > 140:
            continue  
        
        # 在timeDelta内，文字不能重复发送
        timeDelta = pd.Timestamp(now) - pd.Timedelta('30 days')
        if df_text.loc[df_text.index > timeDelta,'text'].str.contains(text).astype('int64').sum() > 0:
            continue
        
        args = {'photo': pic, 'status': text}
        body, headers = fanfou.pack_image(args)
        resp = client.photos.upload(body, headers)
        # df 合并，生成新的df_text
        df_message = pd.DataFrame({'text':text},index = [pd.Timestamp(now)])                
        df_text = pd.concat([df_message,df_text])
        df_text.to_excel('mytext.xlsx')         
                        
        time.sleep(2400)
    except:pass