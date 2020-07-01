import tweepy
import random
import itertools
import schedule
import time

CK = "usi"
CS = "hoge"
AT = "huga"
ATS = "piyo"
auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, ATS)
api = tweepy.API(auth)

a=list(itertools.permutations('うしたぷにきあくん',9))

def usitapu():
    s=a[random.randint(0,len(a)-1)]
    api.update_status('　'.join(s)+'　笑')

schedule.every(30).minutes.do(usitapu)
j=0
while True:
    print('usi',j)
    j+=1
    schedule.run_pending()
    time.sleep(60)