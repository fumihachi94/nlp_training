from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
import time
import pandas as pd
import csv

chrome_driver = './driver/chromedriver/chromedriver.exe'

def get_html_by_bs4(res):
    """
    Retrieve the HTML parser using bs4.

    Requires:
    - To use this function, the following library is required:
      - bs4: `from bs4 import BeautifulSoup`
    """
    charset=res.info().get_content_charset()
    return BeautifulSoup(res.read().decode(charset, 'ignore'), 'html.parser')


def get_tconnect_faq_category_url(URL='https://tconnect.jp/faq/'):
    """
    seleniumを利用してFAQカテゴリURLを取得する\n
    （カテゴリメニューがjsで記述されておりurlopen()で取得したHTMLではカテゴリ情報が取得できないため）
    """

    categories = []

    print('Start Selenium Chrome driver')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    service = ChromeService(executable_path=chrome_driver)
    driver = webdriver.Chrome(options=options, service=service)
    driver.get(URL)
    time.sleep(1)

    elems = driver.find_elements(By.CLASS_NAME,'accordion-child')
    for elem in elems:
        atag_elem = elem.find_element(By.TAG_NAME,'a')
        faq_category_name = atag_elem.get_property('text')
        faq_category_url  = atag_elem.get_property('href')
        print(faq_category_name+": "+faq_category_url)
        category ={
            'category': faq_category_name,
            'url' : faq_category_url
        }
        categories.append(category)
        
    return categories


def sage2csv(categories, save_file_name='data_export'):
    df = pd.DataFrame(categories)
    df.to_csv(save_file_name+'.csv', encoding='utf-8', index=False, quotechar='"', quoting=csv.QUOTE_ALL)
    print('Data successfully exported to CSV file!')


def loadcsv(csv_file_path='./tcon_faq_categories.csv'):
    return pd.read_csv(csv_file_path)


def get_tconnect_faq_no(category_csv_file=''):
    faqs =[]
    if not category_csv_file:
        categories = get_tconnect_faq_category_url()
    else:
        categories = loadcsv(category_csv_file)
    
    for index, category in categories.iterrows():
        print(index, category['category'], category['url'])
        URL = category['url']
        try:
            with urlopen(URL) as res:
                # HTMLドキュメントからBeautifulSoupを初期化
                charset=res.info().get_content_charset()
                soup = BeautifulSoup(res.read().decode(charset, 'ignore'), 'html.parser')
                # FAQリストをピックアップ
                contents = soup.find('ul', class_='article-list')
                items = contents.find_all('li', class_='article-list-item')
                # 各種データを抽出
                for item in items:
                    # FAQの本文を取得
                    fqa_res  = urlopen('https://tconnect.jp'+item.find('a').get('href'))
                    faq_soup = BeautifulSoup(fqa_res.read().decode(charset, 'ignore'), 'html.parser')
                    mainContents = faq_soup.find('div', id='contents-main')
                    # 不要部分を除外
                    try:
                        mainContents.find('h2',  class_='title').decompose()                 # タイトル部分を除外
                        mainContents.find('div', class_='article-num').decompose()           # FAQ No部分を除外
                        mainContents.find('div', class_='category-breadcrumb').decompose()   # カテゴリ部分を削除
                        mainContents.find('h3',  class_='emphasis-title').decompose()        # 関連FAQ部分を除外
                        mainContents.find('ul',  class_='question-list-related').decompose() # 関連FAQ部分を除外
                    except Exception as e:
                        print(f'Error: ', e)
                        pass
                    # print(mainContents.text.replace(' ','').strip(''))
                    # print(''.join(mainContents.text.split()))
                    # table = str.maketrans({
                    # '\u3000': '',
                    # ' ': '',
                    # '\t': '',
                    # '\r': '',
                    # '\n': ''
                    # })
                    # print(mainContents.text.translate(table))

                    # 各種データを格納
                    faq = {
                        'id': item.find(class_='article-info').text[-5:-1],
                        'category': category['category'],
                        'title': item.find('p').text,
                        'url': item.find('a').get('href'),
                        'body': ''.join(mainContents.text.split())
                    }
                    faqs.append(faq)
                    print('[%s] %s: %s, %s' %(faq['id'], faq['category'], faq['title'], faq['url']))

        except Exception as e:
            print(f'Error: ', e)
            pass

    return faqs


def get_tconnect_faq_content(faq_no_list_csv_file=''):
    contents =[]
    if not faq_no_list_csv_file:
        print('Error: csv file path error. 有効なFAQ Noリストのcsvを指定してください。')
    else:
        faq_no_list = loadcsv(faq_no_list_csv_file)


if __name__ == "__main__": 
    # 1. T-Connect FAQサイトからFAQカテゴリ＆URL一覧を取得
    # Seleniumを使ってT-Connect FAQのカテゴリ一覧を取得する際に利用
    if False:
        categories = get_tconnect_faq_category_url(URL='https://tconnect.jp/faq/')
        sage2csv(categories, 'tcon_faq_categories')

    # 2. 1で取得したカテゴリ一覧から全FAQ情報を取得
    if True:
        faqs = get_tconnect_faq_no('./tcon_faq_categories.csv')
        sage2csv(faqs, 'tcon_faq_list_all')
    


        
    




