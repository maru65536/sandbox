import json
import os
import re
import random

import tweepy
import MeCab
from requests_oauthlib import OAuth1Session


CK = "hoge"
CS = "fuga"
AT = "piyo"
ATS = "usi"
auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, ATS)
api = tweepy.API(auth)

#userのツイートを取得し、ツイートID:ツイート内容　という形のdictを作成します。
#dictは既定の場所にJSONとして保存されます。
def tweet_fetch(user):
    #JSONファイルが存在しなかったら自動生成、存在した場合は読み込み
    tweetpath='Sandbox\\{}.json'.format(user)
    if os.path.exists(tweetpath):
        a=json.load(open(tweetpath,'r',encoding='UTF-8'))
    else:
        a={}
    #><を正しく表示して格納
    for tweet in [tweet for tweet in tweepy.Cursor(api.user_timeline,id=user).items()][::-1]:
        a[str(tweet.id)]=tweet.text.replace('\n',' ').replace('&gt;','>').replace('&lt;','<')
    with open(tweetpath,'w',encoding='UTF-8') as f:
        json.dump(a,f,indent=4,ensure_ascii=0)


#userのツイートから、与えられた文字列sを含むものを抽出します。
#urls=Trueで、投稿のURLも同時に出力します。
def tweet_search(user,s,urls=False):
    tweetpath='Sandbox\\{}.json'.format(user)
    if not os.path.exists(tweetpath):
        tweet_fetch(user)
    tweets=json.load(open(tweetpath,'r',encoding='UTF-8'))
    tweetlist=list(tweets.items())
    for tweet in tweets.values():
        if s in tweet:
            id=[id for id,t in tweetlist if t == tweet][0]
            print(tweet)
            if urls:
                print('https://twitter.com/{}/status/{}'.format(user,id))
                print()


def Markov_dic_maker(user,n): #userのn階マルコフ連鎖の辞書を作成し,JSON形式で保存します。
    tweets,Markov_dic=[],{}
    tweetpath='Sandbox\\{}.json'.format(user)
    if not os.path.exists(tweetpath):
        tweet_fetch(user)
    a=json.load(open(tweetpath,'r',encoding='UTF-8'))
    for tweet in a.values():
        #RT、質問箱自動ツイートを除去
        if tweet[0:2]=='RT' or '質問箱' in tweet:
            continue
        #リプとリンクを除去してリストに追加
        tweets.append(' '.join([t for t in list(tweet.split()) if t[0]!='@' and 'http' not in t]))
    #形態素解析して辞書に追加
    for tweet in tweets:
        lines = MeCab.Tagger('Owakati').parse(tweet).split('\n')
        items = list((re.split('[\t]',line)[0] for line in lines))
        for i in range(n,len(items)-1):
            tmp=','.join(items[i-n:i])
            if tmp in Markov_dic:
                Markov_dic[tmp].append(items[i])
            else:
                Markov_dic[tmp]=[items[i]]
    #保存
    with open('Sandbox\\{}m{}dic.json'.format(user,n),'w',encoding='UTF-8') as f:
        json.dump(Markov_dic,f,indent=4,ensure_ascii=0)


#n階マルコフ連鎖で文章を生成します。
#user(twitterID)、階数を指定してください。
#first_wordsを指定する場合は、階数と同じだけのstrを含むlistで渡してください。
def Markov_tweet(user,n,number=10,first_words=False):
    Markovpath='Sandbox\\{}m{}dic.json'.format(user,n)
    if not os.path.exists(Markovpath):
        Markov_dic_maker(user,n)
    Markov_dic=json.load(open(Markovpath,'r',encoding='UTF-8'))
    Markov_key=list(Markov_dic.keys())
    #不正なfirst_wordsを除く
    if first_words and ','.join(first_words) not in Markov_key:
        print('error')
        exit()
    for _ in range(number):
        if not first_words:
            t=list(random.choice(Markov_key).split(','))
        else:
            t=first_words[:]
        while t[-1]!='EOS' and ','.join(t[-n:]) in Markov_dic:
            tmp=t[-n:]
            t.append(random.choice(Markov_dic[','.join(tmp)]))
        print(*t[:-1],sep='',end='\n\n')