import requests
from datetime import datetime, time
import smtplib
import os

# email secrets and emails
MY_EMAIL = os.environ.get("MY_EMAIL")
TO_EMAIL = os.environ.get("TO_EMAIL")
PASSWORD = os.environ.get("PASSWORD")

# stock price api parameters and secrets
STOCK_PRICE_API_KEY = os.environ.get("STOCK_PRICE_API_KEY")
STOCK_SYMBOL = "TSLA"
COMPANY_NAME = "Tesla"
stock_url = "https://www.alphavantage.co/query"
stock_parameters= {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_SYMBOL,
    "apikey": STOCK_PRICE_API_KEY
}

# get current day and previous time data
date_today = datetime.now().date()
date_yesterday = date_today.replace(day=(date_today.day-1))
date_before_yesterday = date_yesterday.replace(day=(date_yesterday.day-1))

# closing date times for api format
closing_time = "T20:00:00"
close_date_yesterday = f"{date_yesterday}{closing_time}"
close_date_before_yesterday = f"{date_before_yesterday}{closing_time}"

# news api information
NEWS_API_KEY = "744a5c4a74d14d2e86ac5a7aa7eda8e0"
news_url = "https://newsapi.org/v2/everything"
news_parameters = {
    "apiKey": NEWS_API_KEY,
    "qInTitle": COMPANY_NAME,
    "from": close_date_before_yesterday,
    "to": close_date_yesterday
}
news_paragraph = ""

# use requests to import data from api
stock_data = requests.get(url=stock_url, params= stock_parameters)
daily_stock_data = stock_data.json()["Time Series (Daily)"]

# get yesterday's closing price and compare to the previous day
yesterday_close_price = float(daily_stock_data[f"{date_yesterday}"]["4. close"])
print(yesterday_close_price)
before_yesterday_close_price = float(daily_stock_data[f"{date_before_yesterday}"]["4. close"])
print(before_yesterday_close_price)
percent_change = abs(round((((yesterday_close_price / before_yesterday_close_price) - 1) * 100), 2))
# if percent change is more than 10% +/- then
if percent_change > 10:
    news_data = requests.get(news_url, params=news_parameters).json()
    articles = news_data["articles"]
    top_articles = articles[:3]
    for article in top_articles:
        news_source = article["source"]["name"]
        article_title = article["title"]
        url = article["url"]
        email_snippet = f"\n\n{news_source}\n{article_title}\n{url}"
        news_paragraph += email_snippet
    print(news_paragraph)
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=TO_EMAIL,
            msg=(f"Subject: Stock Alert {STOCK_SYMBOL}:\n\n"
                 f"{STOCK_SYMBOL} has changed by {percent_change}% from yesterday's closing price to the day before."
                 f"Relevant News Article from the Time Between Change:\n"
                 f"{news_paragraph}".encode('utf-8'))
        )
