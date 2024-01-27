from urllib.request import urlopen
from bs4 import BeautifulSoup
import traceback
import re
import pandas as pd
import csv
from datetime import date, timedelta
import time 

# Livedoor News から情報を取得する
# https://news.livedoor.com/social_reaction/yyyy-mm-dd/ (話題のニュース)
# https://news.livedoor.com/topics/detail/********/ (要約文)
# https://news.livedoor.com/article/detail/********/ (本文)


start_date = date(2023,8,1)   #開始日
end_date   = date(2023,12,31) #終了日

newsdate = ''
month    = start_date.month
year     = start_date.year
articles = []

# 開始日から終了日までループを回す
for i in range((end_date - start_date).days + 1):
    tempdate = start_date + timedelta(i)
    newsdate = str(tempdate)
    print(newsdate)

    # # 月単位でCSVファイルを生成
    # if tempdate.month > month:
    #     df = pd.DataFrame(articles)
    #     # encoding='sjis'だとJupyterLab（CSVTable）上で表示不可なことに注意
    #     df.to_csv('livedoor_news_socialReactionList_'+str(year)+'-'+str(month)+'.csv', encoding='utf-8', index=False, quotechar='"', quoting=csv.QUOTE_ALL)
    #     month = tempdate.month
    #     articles = []

    # 年単位でCSVファイルを生成
    if tempdate.year > year:
        df = pd.DataFrame(articles)
        # encoding='sjis'だとJupyterLab（CSVTable）上で表示不可なことに注意
        df.to_csv('livedoor_news_socialReactionList_'+str(year)+'.csv', encoding='utf-8', index=False, quotechar='"', quoting=csv.QUOTE_ALL)
        year = tempdate.year
        articles = []
    
    # ニュースアクセスランキング（ライブドアニュース）のURL
    URL = 'https://news.livedoor.com/social_reaction/'+newsdate+'/'
    # ニュースID抽出用の正規表現（名前付きグループ）
    REG_URL = r'(?P<L1>(https?://[^/]+/))(?P<L2>([^/]+))/(?P<L3>([^/]+))/(?P<L4>([^/]+))/'

    try:
        with urlopen(URL) as res:
            # HTMLドキュメントからBeautifulSoupを初期化
            soup = BeautifulSoup(res.read().decode('euc_jp', 'ignore'), 'html.parser')
            # 話題のニュースを検索し、ページ内の全権を取得
            socialReactionList = soup.find('ol', class_='socialReactionList').find_all('li')

            for idx, soupNews in enumerate(socialReactionList):
                # aタグがない項目の場合スキップ（Tweet数の列を除外するため）
                if soupNews.a is None: continue
                # 記事のURLを取得
                url = soupNews.a.get('href')
                # NewsBodyを検索し取得
                soupNewsBody = soupNews.find('div', class_='socialReactionBody')
                # NewsBodyから各種データを抽出
                article = {
                    # ニュースIDを3行要約ページURLから抽出
                    'date':newsdate,
                    'id': re.search(REG_URL, url).groupdict()['L4'],
                    # タイトル／サマリ／提供元／公開日時をHTMLタグの本文から抽出
                    'title': soupNewsBody.find('h3', class_='socialReactionTtl').text,
                    # 'summary': soupNewsBody.find('p', class_='socialReactionDesc').text,
                    # 'tweetnum': soupNewsBody.find('i', class_='icon icoTw').text
                }
                articles.append(article)
                print('%s: %s' %(article['id'], soupNewsBody.find('h3', class_='socialReactionTtl').text))

            # time.sleep(1)

    except Exception as e:
        # エラー概要
        print('Exception: ', e)
        print('=====')
        # エラー詳細（スタックトレース）
        print(traceback.format_exc().rstrip())
        print('=====')

df = pd.DataFrame(articles)
# encoding='sjis'だとJupyterLab（CSVTable）上で表示不可なことに注意
df.to_csv('livedoor_news_socialReactionList_'+str(year)+'_fin.csv', encoding='utf-8', index=False, quotechar='"', quoting=csv.QUOTE_ALL)
year = tempdate.year
articles = []