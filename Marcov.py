import tweepy
import json
import MeCab
import re
import random
from requests_oauthlib import OAuth1Session

CK = "hoge"
CS = "fuga"
AT = "piyo"
ATS = "usi"
auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, ATS)
api = tweepy.API(auth)

def tweet_fetch(user):
    tweetpath='Sandbox\\{}.json'.format(user)
    a=json.load(open(tweetpath,'r',encoding='UTF-8'))
    for tweet in [tweet for tweet in tweepy.Cursor(api.user_timeline,id=user).items()][::-1]:
        a[str(tweet.id)]=tweet.text.replace('\n',' ')
    with open(tweetpath,'w',encoding='UTF-8') as f:
        json.dump(a,f,indent=4,ensure_ascii=0)


def tweet_search(user,s,urls=False):
    tweetpath='Sandbox\\{}.json'.format(user)
    tweets=json.load(open(tweetpath,'r',encoding='UTF-8'))
    tweetlist=list(tweets.items())
    for tweet in tweets.values():
        if s in tweet:
            id=[id for id,t in tweetlist if t == tweet][0]
            print(tweet)
            if urls:
                print('https://twitter.com/{}/status/{}'.format(user,id))
                print()


def Markov_dic_maker(user):
    tweets,Markov_dic=[],{}
    #形態素解析可能な形にする
    for tweet in [tweet for tweet in tweepy.Cursor(api.user_timeline,id=user).items()][::-1]:
        #><を正しく表示する
        tweet.text=tweet.text.replace('&gt;','>').replace('&lt;','<')
        #RT、質問箱自動ツイートを除去
        if tweet.text[0:2]=='RT' or '質問箱' in tweet.text:
            continue
        #リプとリンクを除去してリストに追加
        tweets.append(' '.join([t for t in list(tweet.text.split()) if t[0]!='@' and 'http' not in t]))
    #形態素解析して辞書に追加
    for tweet in tweets:
        lines = MeCab.Tagger('Owakati').parse(tweet).split('\n')
        items = list((re.split('[\t]',line)[0] for line in lines))
        for i in range(len(items)-2):
            if items[i] in Markov_dic:
                Markov_dic[items[i]].append(items[i+1])
            else:
                Markov_dic[items[i]]=[items[i+1]]
    #保存
    with open('Sandbox\\{}mdic.json'.format(user),'w',encoding='UTF-8') as f:
        json.dump(Markov_dic,f,indent=4,ensure_ascii=0)


def Markov_tweet(user,number=10,first_word=False):
    Markovpath='Sandbox\\{}mdic.json'.format(user)
    Markov_dic=json.load(open(Markovpath,'r',encoding='UTF-8'))
    Markov_key=list(Markov_dic.keys())
    if first_word and first_word not in Markov_key:
        print('error')
        exit()
    for _ in range(number):
        if not first_word:
            t=random.choice(Markov_key)
        else:
            t=first_word
        while t!='EOS':
            print(t,end='')
            t=random.choice(Markov_dic[t])
        print('\n')
