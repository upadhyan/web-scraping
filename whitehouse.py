import base64
import pandas as pd
import numpy as np
import bs4
import requests
import re
import datetime
def hello_pubsub(event, context):
  file_name = 'gs://prices-store-1/whitehouse.csv'
  df = update_whitehouse_file(file_name)
  if df is not None:
    return "done"
  else:
    return "df is none"
def pull_initial_whitehouse():
  url = 'https://www.whitehouse.gov/briefing-room/statements-releases/'
  response = requests.get(url)
  soup = bs4.BeautifulSoup(response.text, 'html.parser')
  ## get max number of pages: 
  page_numbers = soup.find_all('a', {"class": "page-numbers"})
  numbers = []
  for page in page_numbers:
    numbers.append(int(page.text[4:]))
  last = numbers[-1]
  links = []
  for i in range (1, last + 1):
    url = 'https://www.whitehouse.gov/briefing-room/statements-releases/page/'+str(i)+'/'
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('a', {"class":"news-item__title"}, href=True)
    for article in articles:
      #print(article['href'])
      links.append(article['href'])
  article_content = []
  for i in range(len(links)):
    link = links[i]
    response = requests.get(link)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    article = {
        "title":' '.join(soup.find('h1', {"class":"page-title topper__title news"}).text.split()),
        "date": datetime.datetime.strptime(soup.find('time', {"class":"posted-on entry-date published updated"}).text, "%B %d, %Y"),
        "text": ' '.join(soup.find('section', {"class":"body-content"}).text.split())
    }
    article_content.append(article)
  df = pd.DataFrame(article_content)
  return df.iloc[::-1]
def pull_new_releases():
  url = 'https://www.whitehouse.gov/briefing-room/statements-releases/'
  response = requests.get(url)
  soup = bs4.BeautifulSoup(response.text, 'html.parser')
  links = []
  articles = soup.find_all('a', {"class":"news-item__title"}, href=True)
  for article in articles:
    #print(article['href'])
    links.append(article['href'])
  article_content = []
  for i in range(len(links)):
    link = links[i]
    response = requests.get(link)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    article = {
        "title":' '.join(soup.find('h1', {"class":"page-title topper__title news"}).text.split()),
        "date": datetime.datetime.strptime(soup.find('time', {"class":"posted-on entry-date published updated"}).text, "%B %d, %Y"),
        "text": ' '.join(soup.find('section', {"class":"body-content"}).text.split())
    }
    article_content.append(article)
  df = pd.DataFrame(article_content)
  return df.iloc[::-1]
def update_whitehouse_file(old_file):
  old=pd.read_csv(old_file)
  old = old.dropna()
  old['date'] = pd.to_datetime(old['date'])
  print(old.shape[0])
  new = pull_new_releases()
  df = old.merge(new, how = 'outer', on = 'title')
  df['date'] = df['date_x']
  df['date'] = df['date'].fillna(df['date_y'])
  df['text'] = df['text_x']
  df['text'] = df['text'].fillna(df['text_y'])
  df = df.drop(['text_x', 'text_y', 'date_x', "date_y"], axis = 1)
  print(df.shape[0])
  df.sort_values(by = 'date')
  df.to_csv(old_file, index = False)
  return df