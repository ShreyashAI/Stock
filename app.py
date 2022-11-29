import streamlit as st
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pandas as pd
import plotly
import plotly.express as px
import json 
import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import subprocess
from datetime import datetime
import os

st.set_page_config(page_title = "AI-CP", layout = "wide")


def get_news(ticker):
    url = finviz_url + ticker
    req=Request(url=url,headers={'user-agent': 'my-app'}) 
    response = urlopen(req)    
   
    html = BeautifulSoup(response)
   
    news_table = html.find(id='news-table')
    return news_table

def parse_news(news_table):
    parsed_news = []
    
    for x in news_table.findAll('tr'):
       
        try:
           
            text = x.a.get_text() 
           
            date_scrape = x.td.text.split()
            

            if len(date_scrape) == 1:
                time = date_scrape[0]				
			  
            else:
                date = date_scrape[0]
                time = date_scrape[1]
			
          
            parsed_news.append([date, time, text])        
            
            
        except:
            pass
			
    
    columns = ['date', 'time', 'headline']
   
    parsed_news_df = pd.DataFrame(parsed_news, columns=columns)        
   
    parsed_news_df['datetime'] = pd.to_datetime(parsed_news_df['date'] + ' ' + parsed_news_df['time'])
			
    return parsed_news_df
        
    
        
def score_news(parsed_news_df):

    vader = SentimentIntensityAnalyzer()
    
    
    scores = parsed_news_df['headline'].apply(vader.polarity_scores).tolist()

    scores_df = pd.DataFrame(scores)

   
    parsed_and_scored_news = parsed_news_df.join(scores_df, rsuffix='_right')             
    parsed_and_scored_news = parsed_and_scored_news.set_index('datetime')    
    parsed_and_scored_news = parsed_and_scored_news.drop(['date', 'time'], 1)          
    parsed_and_scored_news = parsed_and_scored_news.rename(columns={"compound": "sentiment_score"})

    return parsed_and_scored_news

def plot_hourly_sentiment(parsed_and_scored_news, ticker):
   
    
    mean_scores = parsed_and_scored_news.resample('H').mean()

  
    fig = px.bar(mean_scores, x=mean_scores.index, y='sentiment_score', title = ticker + ' Hourly Sentiment Scores')
    
    return fig 
def plot_daily_sentiment(parsed_and_scored_news, ticker):
   
   
    mean_scores = parsed_and_scored_news.resample('D').mean()

    fig = px.bar(mean_scores, x=mean_scores.index, y='sentiment_score', title = ticker + ' Daily Sentiment Scores')
    
    return fig

finviz_url = 'https://finviz.com/quote.ashx?t='


st.header("Course Project AI GRP-01")

ticker = st.text_input('Enter Stock Ticker', '').upper()

df = pd.DataFrame({'datetime': datetime.now(), 'ticker': ticker}, index = [0])


try:
	st.subheader("Hourly and Daily Sentiment of {} Stock".format(ticker))
	news_table = get_news(ticker)
	parsed_news_df = parse_news(news_table)
	print(parsed_news_df)
	parsed_and_scored_news = score_news(parsed_news_df)
	fig_hourly = plot_hourly_sentiment(parsed_and_scored_news, ticker)
	fig_daily = plot_daily_sentiment(parsed_and_scored_news, ticker) 
	 
	st.plotly_chart(fig_hourly)
	st.plotly_chart(fig_daily)

	
	st.table(parsed_and_scored_news)
	
except Exception as e:
	print(str(e))
	st.write("Enter a correct stock ticker, e.g. 'AMZN' above and hit Enter.")	

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 