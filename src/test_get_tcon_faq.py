from urllib.request import urlopen
from bs4 import BeautifulSoup
import traceback
import re
import pandas as pd
import csv
from datetime import date, timedelta
import time 

# T-Connect FAQページから情報を取得する
# <https://tconnect.jp/faq/{各カテゴリの階層}/****.html>
# Point1 - ****にはFAQ No.が入る（4桁固定） 
# Point2 - 各カテゴリの階層はわからないのでTOPページのメニューリンクから取得する

faqs = []

# 1~9999までループを回す
for n in range(1001, 1002):
    # 4桁のFAQ No.用に変換
    faqNum = '{:04d}'.format(n)
    print('FAQ-'+faqNum)

    # T-Connect FAQページのURL
    URL = 'https://tconnect.jp/faq/application/howtoappli/'+faqNum+'.html'

    try:
        with urlopen(URL) as res:
            # HTMLドキュメントからBeautifulSoupを初期化
            charset=res.info().get_content_charset()
            soup = BeautifulSoup(res.read().decode(charset, 'ignore'), 'html.parser')
            # メイン部分をピックアップ
            mainContents = soup.find(id='contents-main')
            # 各種データを抽出
            faq = {
                'id': faqNum,
                'category': mainContents.find(class_='category-breadcrumb').text,
                'title': mainContents.find('h2', class_='title').text,
            }
            faqs.append(faq)
            print('%s: %s' %(faq['category'], faq['title']))

    except Exception as e:
        print(f'Error: ', e)
        pass
