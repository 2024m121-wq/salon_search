#!/usr/bin/env python
# coding: utf-8

# # Pandasで美容院データを読み込み・加工・分析

# ## ファイルの読み込みと確認

# In[ ]:


import pandas as pd
pd.set_option('display.max_columns', None)  # 表示オプションの設定（列数の制限解除）

salon_df = pd.read_csv("salon.csv")

print("salon.csvの先頭")
salon_df.head(5)


# In[ ]:


detail_df = pd.read_csv("detail.csv")

print("detail.csvの先頭")
detail_df.head(5)


# ## ２つのファイルを結合する準備
# 主キーとしてURLから店舗IDを抽出する

# In[ ]:


# 店舗IDを抽出する関数
import re

def extract_store_id(link):
    match = re.search(r'slnH\d+', link)
    if match:
        return match.group(0)
    else:
        return None


# In[ ]:


# 関数の動作を確認
extract_store_id("https://beauty.hotpepper.jp/slnH000658911/")


# In[ ]:


extract_store_id("https://beauty.hotpepper.jp/slnH000658911/?cstt=1")


# ## 関数を利用して各テーブルにstore_id列を作成する

# In[ ]:


# 関数を適用してstore_id列を作成する
salon_df["store_id"] = salon_df["link"].apply(extract_store_id)
detail_df["store_id"] = detail_df["link"].apply(extract_store_id)


# In[ ]:


salon_df.head(5)


# In[ ]:


detail_df.head(5)


# ## 重複チェック

# In[ ]:


salon_df['store_id'].duplicated().sum()


# In[ ]:


salon_df[salon_df['store_id'].duplicated(keep=False)] #重複している店舗の確認


# In[ ]:


salon_df = salon_df.drop_duplicates(subset='store_id', keep='first')
# 重複するレコードは最初の1件を残して削除


# In[ ]:


salon_df['store_id'].duplicated().sum()  # 再び重複チェック


# In[ ]:


detail_df['store_id'].duplicated().sum()
# detail_dfについても重複チェックを行ったところ、重複が存在しなったため、特別な処理は不要


# ## 主キーを利用して２つのテーブルを結合する

# In[ ]:


print(salon_df.columns)


# In[ ]:


print(detail_df.columns)


# In[ ]:


merged_df = pd.merge(salon_df, detail_df, on="store_id", how="left", suffixes=("_salon", "_detail"))


# In[ ]:


print(merged_df.columns)


# In[ ]:


merged_df.head(3)


# ## データ型の確認と前処理

# In[ ]:


print(merged_df.info())


# In[ ]:


print(merged_df.isnull().sum())


# ## 欠損処理
# 店舗ブログは欠損していても問題ないので放置する
# star（平均星評価）, review（口コミ数）が欠損している店は今回は除外する

# In[ ]:


merged_df[merged_df["review"].isnull()]
#linkのURLをブラウザに貼り付けて確認してみる
#まだ口コミがありません。


# In[ ]:


merged_df[merged_df["star"].isnull()]
#linkのURLをブラウザに貼り付けて確認してみる
#※1年以内の口コミ投稿がないため、平均点を表示していません。
#まだ口コミがありません。


# In[ ]:


merged_df = merged_df.dropna(subset=["star", "review"])


# In[ ]:


merged_df.info()


# # データ型の確認と前処理

# ### seatsの数値化

# In[ ]:


merged_df['seats']


# In[ ]:


merged_df['seats'] = pd.to_numeric(
    merged_df['seats']
    .astype(str)
    .str.extract(r'セット面(\d+)席')[0],
    errors="coerce"
).astype(float)


# In[ ]:


merged_df['seats']


# ### review（口コミ数）の数値化

# In[ ]:


merged_df["review"]


# In[ ]:


merged_df["review"] = pd.to_numeric(
    merged_df["review"]
    .astype(str)
    .str.extract(r'（(\d+)件）')[0],
    errors="coerce"
).astype(float)


# In[ ]:


merged_df["review"]


# ### priceの数値化

# In[ ]:


merged_df['price']


# In[ ]:


merged_df['price'] = pd.to_numeric(
    merged_df['price']
    .astype(str)
    .str.replace("￥","",regex=False)
    .str.replace(",","", regex=False)
    .str.replace("～","",regex=False),
    errors="coerce"
).astype(float)


# In[ ]:


merged_df['price']


# # 人気スコアの作成
# レビューが多くて、平均星評価が高い店舗が人気があると想定する

# In[ ]:


import numpy as np

merged_df['pop_score']=merged_df['star']* np.log1p(merged_df['review'])


# In[ ]:


print(merged_df.columns)


# In[ ]:


merged_df['pop_score']


# # 並べ替えと絞り込み

# In[ ]:


sorted_by_star = merged_df.sort_values(by='star',ascending=False)
print('平均星評価順上位10件')
sorted_by_star[['store_id','name_salon','star','review','pop_score','price','seats']].head(10)


# In[ ]:


sorted_by_pop_score = merged_df.sort_values(by='pop_score', ascending=False)
print('人気スコア上位10件')
sorted_by_pop_score[['store_id','name_salon','star','review','pop_score','price','seats']].head(10)


# # Plotlyで可視化

# In[ ]:


import plotly.express as px
px.histogram(merged_df, x='price') # 価格のヒストグラム


# In[ ]:


px.scatter(merged_df, x='pop_score', y='price', hover_data=['name_salon']) # 人気スコアと価格の散布図


# # データ保存

# In[ ]:





# In[ ]:


merged_df.columns


# In[ ]:


# 残す列と、その列の並びを明示的に指定して保存
columns_order=['store_id','name_salon','slncatch',
               'star','review','pop_score',
               'price','seats',
               'address','access','link_detail']
merged_df[columns_order].to_csv('merged.csv', index=False)

streamlit run "salon_analysis (1).py"
