#!/usr/bin/env python
# coding: utf-8

# # Pandasで美容院データを読み込み・加工・分析

# ## ファイルの読み込みと確認

# In[2]:


import pandas as pd
pd.set_option('display.max_columns', None) # 表示オプションの設定（列数の制限解除）

salon_df = pd.read_csv("merged11.csv")

print("salon.csvの先頭") # ここは文字なのでそのままで大丈夫です
salon_df.head(5)


# In[3]:


detail_df = pd.read_csv("detail.csv")

print("detail.csvの先頭")
detail_df.head(5)


# ## ２つのファイルを結合する準備
# 主キーとしてURLから店舗IDを抽出する

# In[4]:


# 店舗IDを抽出する関数
import re

def extract_store_id(link):
    match = re.search(r'slnH\d+', link)
    if match:
        return match.group(0)
    else:
        return None


# In[5]:


# 関数の動作を確認
extract_store_id("https://beauty.hotpepper.jp/slnH000658911/")


# In[6]:


extract_store_id("https://beauty.hotpepper.jp/slnH000658911/?cstt=1")


# ## 関数を利用して各テーブルにstore_id列を作成する

# In[42]:


# 1. まず detail_df（下の表）の列名を日本語から英語に変換する
detail_df = detail_df.rename(columns={
    '名前': 'name',
    'リンク': 'link',
    '星': 'star',
    'レビュー': 'review',
    '住所': 'address'
})

# 2. urlからIDを抜き出す関数を定義する
def extract_store_id(url):
    return url.split('/')[-2]

# 3. detail_df 側にだけ store_id を新しく作成する
detail_df["store_id"] = detail_df["link"].apply(extract_store_id)


# In[43]:


print(detail_df.columns)


# In[44]:


print(salon_df.columns)


# In[45]:


salon_df.head(5)


# In[46]:


detail_df.head(5)


# ## 重複チェック

# In[47]:


salon_df['store_id'].duplicated().sum()


# In[48]:


salon_df[salon_df['store_id'].duplicated(keep=False)] #重複している店舗の確認


# In[49]:


salon_df = salon_df.drop_duplicates(subset='store_id', keep='first')
# 重複するレコードは最初の1件を残して削除


# In[50]:


salon_df['store_id'].duplicated().sum()  # 再び重複チェック


# In[51]:


# detail_dfの列名を英語に変換し、store_idを作成する
detail_df = detail_df.rename(columns={
    '名前': 'name',
    'リンク': 'link',
    '星': 'star',
    'レビュー': 'review',
    '住所': 'address'
})

# urlからIDを抜き出す関数
def extract_store_id(url):
    return url.split('/')[-2]

# 重複チェックの前にstore_idを作っておく
detail_df['store_id'] = detail_df['link'].apply(extract_store_id)

# テキストの元の処理（重複チェック）
detail_df['store_id'].duplicated().sum()


# In[52]:


print(salon_df.columns)


# ## 主キーを利用して２つのテーブルを結合する

# In[53]:


print(salon_df.columns)


# In[54]:


print(detail_df.columns)


# In[55]:


merged_df = pd.merge(salon_df, detail_df, on="store_id", how="left", suffixes=("_salon", "_detail"))


# In[56]:


# urlからIDを抜き出す関数を定義
def extract_store_id(url):
    return url.split('/')[-2]

# 合体する前に、detail_dfにもstore_idを新しく作ってあげる
detail_df['store_id'] = detail_df['link'].apply(extract_store_id)

# ２つのテーブルを結合する（元の処理）
merged_df = pd.merge(salon_df, detail_df, on="store_id", how="left", suffixes=("_salon", "_detail"))


# In[57]:


print(merged_df.columns)


# In[58]:


merged_df.head(3)


# ## データ型の確認と前処理

# In[59]:


print(merged_df.info())


# In[60]:


print(merged_df.isnull().sum())


# ## 欠損処理
# 店舗ブログは欠損していても問題ないので放置する
# star（平均星評価）, review（口コミ数）が欠損している店は今回は除外する

# In[64]:


# 修正後のコード
merged_df[merged_df["review_detail"].isnull()]


# In[65]:


# 修正後のコード
merged_df = merged_df.dropna(subset=["star_salon", "review_detail"])


# In[67]:


# フォルダパスを挟まず、ファイル名だけで直接保存する
merged_df.to_csv("salon_analysis.csv", index=False)


# In[68]:


merged_df.info()


# # データ型の確認と前処理

# ### seatsの数値化

# In[69]:


merged_df['seats']


# In[70]:


merged_df['seats'] = pd.to_numeric(
    merged_df['seats']
    .astype(str)
    .str.extract(r'セット面(\d+)席')[0],
    errors="coerce"
).astype(float)


# In[71]:


merged_df['seats']


# ### review（口コミ数）の数値化

# In[74]:


# 修正後のコード
merged_df["review_detail"]


# In[75]:


# 修正後のコード（review を review_detail に変更）
merged_df["review_detail"] = pd.to_numeric(
    merged_df["review_detail"].astype(str).str.extract(r'（(\d+)件）')[0], 
    errors="coerce"
).astype(float)


# In[77]:


# 修正後のコード（review を review_detail に変更）
merged_df["review_detail"]


# ### priceの数値化

# In[78]:


merged_df['price']


# In[79]:


merged_df['price'] = pd.to_numeric(
    merged_df['price']
    .astype(str)
    .str.replace("￥","",regex=False)
    .str.replace(",","", regex=False)
    .str.replace("～","",regex=False),
    errors="coerce"
).astype(float)


# In[80]:


merged_df['price']


# # 人気スコアの作成
# レビューが多くて、平均星評価が高い店舗が人気があると想定する

# In[84]:


import numpy as np
merged_df['pop_score'] = merged_df['star_salon'] * np.log1p(merged_df['review_detail'])


# In[85]:


print(merged_df.columns)


# In[86]:


merged_df['pop_score']


# # 並べ替えと絞り込み

# In[88]:


import numpy as np
merged_df['pop_score'] = merged_df['star_salon'] * np.log1p(merged_df['review_detail'])


# In[90]:


# ファイル名だけで直接保存する
merged_df.to_csv("salon_analysis.csv", index=False)


# # Plotlyで可視化

# In[91]:


import plotly.express as px
px.histogram(merged_df, x='price') # 価格のヒストグラム


# In[92]:


px.scatter(merged_df, x='pop_score', y='price', hover_data=['name_salon']) # 人気スコアと価格の散布図


# # データ保存

# In[93]:


merged_df.columns


# In[95]:


# フォルダのパスを消して、ファイル名だけで直接保存する
merged_df.to_csv("salon.csv", index=False)

