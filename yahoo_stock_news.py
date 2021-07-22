import json
import re
import requests
import datetime
import numpy as np
import pandas as pd
def hello_world(event, context):
  file_name = 'gs://prices-store-1/yahoo.csv'
  df = update_file(file_name)
  if (df is not None):
    print('df is not None')
    return str(df.shape[0])
  else:
    print('something went wrong, df is none')
    return "-1"
def pull_new_articles():
  response = requests.get("https://finance.yahoo.com/topic/stock-market-news")
  root_json_raw = re.search("\.main\s+=\s+(.+);", response.text).group(1)
  root_json = json.loads(root_json_raw) # Parse entire root context as JSON
  # Parse page JSON for stuff like initial articles, fetch crumb ID, etc.
  fetch_crumb = root_json["context"]["plugins"]["FetchrPlugin"]["xhrContext"]["crumb"]
  articles_parent = root_json["context"]["dispatcher"]["stores"]["StreamStore"]["streams"]
  two_keys = list(articles_parent.keys()) # Two different keys, choose one starting with "LIST"
  list_key =  two_keys[0] if "LIST" in two_keys[0] else two_keys[1]
  articles_stream = articles_parent[list_key]["data"] # Should start with LIST?
  articles = list([{ # Articles from initial page
      "title": article["title"],
      "id": article["id"],
      "description": article["summary"],
      "tickers": list([data["symbol"] for data in (article["finance"]["stockTickers"] if article["finance"]["stockTickers"] != None else [])]),
      "time": datetime.datetime.fromtimestamp(article["pubtime"] / 1e3),
  } for article in articles_stream["stream_items"]])
  for article in articles:
    article['tickers'] = ' '.join(article['tickers'])
  df = pd.DataFrame(articles)
  return df.iloc[::-1]
def update_file(old_file):
  old=pd.read_csv(old_file)
  old = old.dropna()
  new = pull_new_articles()
  print(new.tail(11))
  df = pd.concat([old, new]).drop_duplicates(subset='id', keep="first")
  print(df.tail(11))
  df = df.dropna()
  df.to_csv(old_file, index = False)
  return df