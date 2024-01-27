from urllib.request import urlopen
from bs4 import BeautifulSoup
import traceback
import re

# Livedoor News から情報を取得する
# https://news.livedoor.com/social_reaction/yyyy-mm-dd/ (話題のニュース)
# https://news.livedoor.com/topics/detail/********/ (要約文)
# https://news.livedoor.com/article/detail/********/ (本文)

year = '2024'
month = '01'
day = '11'

# ニュースアクセスランキング（ライブドアニュース）のURL
URL = 'http://news.livedoor.com/ranking/'
# ニュースID抽出用の正規表現（名前付きグループ）
REG_URL = r'(?P<L1>(https?://[^/]+/))(?P<L2>([^/]+))/(?P<L3>([^/]+))/(?P<L4>([^/]+))/'

# r = requests.get('https://news.livedoor.com/social_reaction/'+year+'-'+month+'-'+day+'/')
# res = requests.get('https://news.livedoor.com/topics/detail/25679990/')
# res.raise_for_status()


# print('https://news.livedoor.com/social_reaction/'+year+'-'+month+'-'+day+'/')
print(urlopen(URL))

try:
    with urlopen(URL) as res:
        # HTMLドキュメントからBeautifulSoupを初期化
        soup = BeautifulSoup(res.read().decode('euc_jp', 'ignore'), 'html.parser')
        # ニュースアクセスランキング部分を検索し、全て（20件）を取得
        soupNewsRanking = soup.find('ol', class_='articleList withRanking').find_all('li')

        print(soupNewsRanking)

        articles = []
        for idx, soupNews in enumerate(soupNewsRanking):
            # 3行要約ページURLをHTMLタグの属性から抽出
            url = soupNews.a.get('href')
            # NewsBodyを検索し取得
            soupNewsBody = soupNews.find('div', class_='articleListBody')
            # NewsBodyから各種データを抽出
            article = {
                'url': url,
                # ニュースIDを3行要約ページURLから抽出
                'id': re.search(REG_URL, url).groupdict()['L4'],
                # タイトル／サマリ／提供元／公開日時をHTMLタグの本文から抽出
                'title': soupNewsBody.find('h3', class_='articleListTtl').text,
                'summary': soupNewsBody.find('p', class_='articleListSummary').text,
                'vender': soupNewsBody.find('p', class_='articleListVender').text,
                'datetime': soupNewsBody.find('time', class_='articleListDate').text
            }
            articles.append(article)
            print('%2d: %s' %(idx + 1, soupNewsBody.find('h3', class_='articleListTtl').text))
            

        # df = pd.DataFrame(articles)
        # # DataFrameからCSVファイルを生成
        # # encoding='sjis'だとJupyterLab（CSVTable）上で表示不可なことに注意
        # df.to_csv('livedoor_news_ranking.csv', encoding='utf-8', index=False, quotechar='"', quoting=csv.QUOTE_ALL)
except Exception as e:
    # エラー概要
    print('Exception: ', e)
    print('=====')
    # エラー詳細（スタックトレース）
    print(traceback.format_exc().rstrip())
    print('=====')