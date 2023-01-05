#!/usr/bin/env python
# coding: utf-8

# In[1]:

#webスクレイピングのためライブラリとモジュールのインストール
from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep
import re
import requests



# In[2]:

#ブラウザーの取得
browser = webdriver.Chrome('chromedriver.exe')
browser.get('https://tdrnavi.jp/park/tdl/dining/')


# In[3]:

#Beautiful Soup でサイトのデータを抽出
soup = BeautifulSoup(browser.page_source, "html.parser")
# In[21]:


ranks = []
names = []
scores = []
URLs = []
Tag = []

for page in range(1,4):
    url = 'https://tdrnavi.jp/park/tdl/dining/?pageID={}'.format(page)
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, "html.parser")

       #ランキング順位の抽出
    elms = soup.find_all('div',class_='rank')
    for _rank in elms:
        ranks.append(_rank.string)

    #レストランの名前
    elms = soup.select('li h2')
    for _name in elms:
        names.append(_name.string)
    
    #スコア
    elms =soup.find_all('strong',class_ = 'reviewScoreNum')
    for _score in elms:
        scores.append(_score.string)
# In[22]:

#各飲食店のURLの抽出
URLs =[]

for page in range(1,4):
    url = 'https://tdrnavi.jp/park/tdl/dining/?pageID={}'.format(page)
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    
   
    elms = soup.find_all('a',class_ = 'box') # URLからジャンプしてタグを抽出
    for elem in elms :
        _url = elem.attrs['href']
        URLs.append('https://tdrnavi.jp'+_url)


# In[23]:

#抽出したURLのページからタグを習得
Tag = []
for url in URLs:
    items = []
    url_res = requests.get(url)
    url_soup = BeautifulSoup(url_res.text,'html.parser')
    url_selects = url_soup.select('div.spotSubBox span.tag')
    for _tags in url_selects:
        items.append(_tags.string)
    Tag.append(items)


# In[67]:

#抽出したURLのページから各飲食店の概要を習得
Comments = []
for url in URLs:
    items = []
    url_res = requests.get(url)
    url_soup = BeautifulSoup(url_res.text,'html.parser')
    url_comments = url_soup.select('p')
    Comments.append(url_comments[0].string)

# In[24]:
#データフレームをpandasで作成する

import pandas as pd


# In[25]:

#データフレームをそろえるために、データのリストを修正


for Tag_greeting in Tag:
    if 'グリーティング'in Tag_greeting:
        print(Tag_greeting)
    else:
        Tag_greeting.insert(2,'グリーティングなし')


# In[26]:


for Tag_price in Tag:
   if '価格 $' in Tag_price:
            print (Tag_price)
   elif'価格 $$' in Tag_price:
       print (Tag_price)
  
   elif'価格 $$$' in Tag_price:
       print (Tag_price)
   else: 
       Tag_price.insert(3,'価格 --')


# In[27]:


for Tag_rain in Tag:
    if '雨でもOK' in Tag_rain:
        print(Tag_rain)
    else: Tag_rain.insert(4,'雨NG')


# In[28]:

#飲食店のランキング順位、名前、食事の方法をデータフレームに入力。
df =pd.DataFrame()

df['順位']= ranks
df['レストランの名前']= names
df=df.drop(df.index[[43]]) #44番目の店舗のレビューが不完全だったため表から削除。


# In[29]:

#評価点数のデータフレーム作成し、順位・名前のデータフレームと結合する。
df_scores = pd.DataFrame(scores)
df_scores.columns=['点数']

df=pd.concat([df,df_scores],axis=1)


# In[30]:
#タグのデータフレームを作成し、ランキングのデータフレームに結合する。

df_tags = pd.DataFrame(Tag)
df_tags = df_tags.drop(df_tags.columns[[0]],axis = 1)

name = ['スタイル','グリーティング','価格','雨天時','場所']
df_tags.columns = name 
df_tags=df_tags.drop(df_tags.index[[43]])

df=pd.concat([df,df_tags],axis=1)

# In[32]:

#グリーティングと雨天時のデータフレームの名前の修正
greet_list = {
    'グリーティング':'あり',
    'グリーティングなし':'なし'
    }

rain_list ={
    '雨でもOK':'OK',
    '雨NG':'NG'
}


price_list ={
    '価格 $':'安い',
    '価格 $$':'普通',
    '価格 $$$':'高い',
    '価格 --':'不明'
}

df['グリーティング']= df['グリーティング'].replace(greet_list)
df['グリーティング'].value_counts()

df['雨天時']= df['雨天時'].replace(rain_list)
df['雨天時'].value_counts()

df['価格']= df['価格'].replace(price_list)
df['価格'].value_counts()
# In[73]:

#飲食店の概要をデータフレームに結合
df_comments = pd.DataFrame()
df_comments['飲食店の詳細']= Comments
df_comments=df_comments.drop(df_comments.index[[43]])

df= pd.concat([df,df_comments],axis=1)
# In[36]:
#順位のフレームを削除

del df['順位']


# In[37]:
#グラフ作成のためのライブラリを読み込む

import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os


# In[38]:

#データフレームをcsvに出力
df.to_csv('disneyland.csv',index=False,encoding = 'shift jis')


# In[39]:


df.info()
df['場所'].value_counts()


# In[40]:


df['点数']= df['点数'].astype(float)

# In[44]:
#雨天時、グリーティング、食事スタイルをエリア別の棒グラフ

import matplotlib
matplotlib.rcParams['font.family'] = 'MS gothic'

fig,axes = plt.subplots(3,1,figsize = (18,15))
sns.countplot(x = '場所',hue='雨天時',data = df,palette = 'Set2',ax=axes[0])
sns.countplot(x='場所',hue = 'グリーティング',data=df,palette = 'Set2',ax= axes[1])
sns.countplot(x = '場所',hue = 'スタイル',data =df,palette = 'Set2',ax=axes[2])
plt.show()


# In[76]:

#特に飲食店が多いエリアでデータを比較した。
df[df['場所']=='ファンタジーランド']
df[df['場所']=='アドベンチャーランド']
df[df['場所']== 'トゥモローランド']

# In[80]:
#食事スタイルがテーブル（レストラン形式）の飲食店についてデータを見てみる

df[df['スタイル']=='テーブル']
# In[98]:

#エリアと点数の棒グラフ
plt.figure(figsize = (20,20))
g=sns.displot(data = df,x='点数',col='場所',height=4,col_wrap=4,facet_kws=dict(margin_titles=True))
plt.show()


# In[47]:

#雨天時の可不可と評価点数の棒グラフ
plt.figure(figsize = (10,20))
g=sns.displot(data = df,x='点数',col='雨天時',height=4,facet_kws=dict(margin_titles=True))
plt.show()


# In[104]:

#エリア別の飲食店の点数平均の箱ひげ図
plt.figure(figsize = (15,5))
sns.boxplot(data = df,x= '場所',y= '点数',linewidth = 1,palette = 'Set2')
plt.show()



file = open('disneyland.csv')
