import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import csv
import re
from nltk.corpus import stopwords
import pymorphy2

morph = pymorphy2.MorphAnalyzer()
stops = set(stopwords.words("english")) | set(stopwords.words("russian"))


def review_to_wordlist(review):
    # 1)
    review_text = re.sub("[^а-яА-Яa-zA-Z]", " ", review)
    # 2)
    words = review_text.lower().split()
    # 3)
    words = [w for w in words if not w in stops]
    # 4)
    words = [morph.parse(w)[0].normal_form for w in words]
    return (words)


def get_full_page(link):
    driver = webdriver.Chrome("chromedriver")
    driver.get(link)
    pause_time = 3
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    time.sleep(pause_time)
    soup = BeautifulSoup(driver.page_source, "lxml")
    return soup


def get_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    return soup


def get_text(html):
    elements = html.find_all("a", class_="entry_content__link")
    all_texts = []
    pause_time = 60
    i = 0
    for elem in elements:
        if i % 500 == 0:
            time.sleep(pause_time)
        i += 1
        new_html = get_html(elem.get('href'))
        try:
            texts = new_html.find("div", class_="b-article").find_all('p')
            # write_text_to_file(texts)
            text_length = 0
            cur_text = ''
            for text in texts:
                text_length += len(str(text))
                cur_text += str(text)[3:-4]+' '
        except AttributeError:
            text_length = 0
            cur_text = ''
        text = []
        #text = review_to_wordlist(cur_text)
        result = {'length': text_length, 'text': cur_text}
        all_texts.append(result)
    return all_texts


def get_variables(html):
    elements = html.find_all("div", class_="entry_footer entry_footer--short l-pt-16 l-pb-16 lm-pt-12 lm-pb-14")
    all_variables = []
    texts = get_text(html)
    i = 0
    size = []
    content = []
    for text in texts:
        size.append(text['length'])
        content.append(text['text'])
    for elem in elements:
        try:
            likes = elem.find("span", class_="vote__value__v vote__value__v--real").text
            likes = likes.replace(" ", '')
            likes = int(likes)
        except ValueError:
            likes = 0
        except AttributeError:
            likes = 0
        try:
            comments = elem.find("span", class_="comments_counter__count__value l-inline-block l-va-middle").text
            comments = comments.replace(" ", '')
        except AttributeError:
            comments = 0
        try:
            favorite = elem.find("div", class_="favorite_marker__count").text
            favorite = favorite.replace(" ", '')
        except AttributeError:
            favorite = 0
        result = {'likes': likes, 'comments': comments, 'favorite': favorite, 'size': size[i], 'text': content[i]}
        i += 1
        all_variables.append(result)
    return all_variables


def write_to_file(variables):
    #i = 0
    # = {1: 'likes', 2: 'coms', 3: 'favs', 4: 'size', 5: 'text'}
    for variable in variables:
        with open('test2.tsv', 'a', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            #if i == 0:
                #writer.writerow((name_of_rows[1],
                          #       name_of_rows[2],
                          #       name_of_rows[3],
                         #        name_of_rows[4],
                         #        name_of_rows[5]))
                #i = 1
            writer.writerow((variable['likes'],
                             variable['comments'],
                             variable['favorite'],
                             variable['size'],
                             variable['text']))


# def write_text_to_file(text):
#   with open('texts.csv', 'a') as f:
#      writer = csv.writer(f)
#     writer.writerow(text)

link = 'https://dtf.ru/u/210-daniil-ilyasov'
page = get_full_page(link)
write_to_file(get_variables(page))