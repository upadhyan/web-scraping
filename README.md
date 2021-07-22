# web-scraping

This repo contains multiple scripts that can be mounted onto a GCP Cloud function to scrape data from various websites. Currently, the websites on this repo include
<ul>
  <li>Whitehouse Press Releases (whitehouse.py): https://www.whitehouse.gov/briefing-room/statements-releases/</li>
  <li>Yahoo Stock Market News (yahoo_stock_news.py): https://finance.yahoo.com/topic/stock-market-news</li>
</ul>

All these functions persist to a storage bucket, and run periodically to collect new data. To get access to collected data, contact nakulupadhya1@gmail.com
