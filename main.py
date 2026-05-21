import requests
from datetime import datetime, time
import smtplib

# email secrets and emails
MY_EMAIL = "dylansteggerda@gmail.com"
TO_EMAIL = "steggerda.dylan@outlook.com"
PASSWORD = "ppaqaowbcbaxgiae"

# stock price api parameters and secrets
STOCK_PRICE_API_KEY = "6YU3HRAE5XOPBWYM"
STOCK_SYMBOl = "TSLA"
stock_url = "https://www.alphavantage.co/query"
stock_parameters= {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_SYMBOl,
    "apikey": STOCK_PRICE_API_KEY
}

# get current day and previous time data
date_today = datetime.now().date()
date_yesterday = date_today.__replace__(day=(date_today.day-1))
date_before_yesterday = date_yesterday.__replace__(day=(date_yesterday.day-1))

# closing date times for api format
closing_time = "T20:00:00"
close_date_yesterday = f"{date_yesterday}{closing_time}"
close_date_before_yesterday = f"{date_before_yesterday}{closing_time}"

# news api information
NEWS_API_KEY = "744a5c4a74d14d2e86ac5a7aa7eda8e0"
news_url = "https://newsapi.org/v2/everything"
news_parameters = {
    "apiKey": NEWS_API_KEY,
    "q": STOCK_SYMBOl,
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
percent_change = round((((yesterday_close_price / before_yesterday_close_price) - 1) * 100), 2)
# if percent change is more than 10% +/- then
if percent_change > 1 or percent_change < -1:
    news_data = requests.get(news_url, params=news_parameters).json()
    for article in news_data["articles"]:
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
            msg=(f"Subject: Stock Alert {STOCK_SYMBOl}:\n\n"
                 f"{STOCK_SYMBOl} has changed by {percent_change}% from yesterday's closing price to the day before."
                 f"Relevant News Article from the Time Between Change:\n"
                 f"{news_paragraph}".encode('utf-8'))
        )
