# Import mplfinance to plot candlestick graph (uncomment if needed)
# pip install mplfinance
# Import yfinance to draw stock data (uncomment if needed)
# pip install yfinance

# Import stock data collection module
import yfinance as yf
# Import data analysis modules
import pandas as pd
import datetime
# Import visualization modules
import mplfinance as mpf
# Import file organisation modules
import os
import shutil
# Import image recognition modules
#from detect_save_label import run
from detect import run
# Import streamlit
import streamlit as st


################################
####### Define variables #######
################################

#100 day chart
step = 100
# start date = today-100
start_date = (datetime.date.today() - datetime.timedelta(days = 200)).strftime("%Y-%m-%d")
# end date = today
end_date = datetime.date.today().strftime("%Y-%m-%d")
# save path of all elements
save_path = os.getcwd()




###################################
#CHANGE DIRECTORY HERE#############
###################################
# yolo weight path
weight = save_path + '/best.pt'

###############################
########## Functions ##########
###############################

######################################################################
############## Get today stock data from yfinance ####################
######################################################################
# get last close price
def get_now_data(stock):
  #yf.pdr_override() 
  today_data = yf.download(tickers=stock,period='1d',interval='1m') 
  last_close = round(today_data.iloc[-1]["Close"],2)
  last_close_date = today_data.index[-1].strftime("%Y-%m-%d, %H:%M:%S")
  st.metric(label = "Lastest stock price: "+last_close_date ,value = last_close)
  
  #set a global variable to store the current price
  global CURRENT_PRICE 
  CURRENT_PRICE = last_close

######################################################################
################# Get stock data from yfinance #######################
######################################################################
# download prices from yahoo finance and save as df
def get_stock_data(stock,start_date,end_date):
  df = yf.download(stock, start=start_date, end = end_date) 
  # drop the 'Adj Close' since this is not required for plotting the candlestick chart
  df = df.drop('Adj Close',axis=1)
  st.write('Past 5 days trend')
  st.dataframe(df.tail(5))
  return df

######################################################################
############ Plot candlestick graph with 5 fake candles ##############
######################################################################
def plot_fake_candles_chart(stock,latest_95): #latest_95 = df[-step+5:]   

  # add 5 fake records at the bottom of same info as of day95
  for i in range(5):
    latest_95.loc[latest_95.index[-1] + datetime.timedelta(days = 1)] = latest_95.iloc[-1]

  # layout setting of the candlestick graph
  mc = mpf.make_marketcolors(up='#00ff00',down='#ff0000') # green:'#00ff00'; red:'#ff0000'
  s  = mpf.make_mpf_style(marketcolors=mc,facecolor='#B8B8B8') # set the background to grey for easier labelling

  #title of graph = stock ticker + first day + last day + number of days on the chart
  title = stock + ' '+ str(latest_95.index[0].date())+' to '+ str(latest_95.index[-1-5].date()) + ' (' + str(len(latest_95)-5) + ' Days)'

  #chart save path
  #chart_location = save_path + title
  
  # plot graph
  fig, ax = mpf.plot(latest_95,type='candle',figsize=(20,10),title=title,style=s, \
  #need the following in order to return the graph
  returnfig=True) #, savefig=chart_location)

  #set a global variable to store the fake chart name
  #so that we can delete it afterwards
  global CHART_TITLE 
  CHART_TITLE = title
  fig.savefig(title+'.png')

######################################################################
########################### Recommendation ###########################
######################################################################
def buy_or_sell(user_action):
  # define action by user_action in streamlit
  if user_action == 'buy':
    action = '0'
  elif user_action == 'sell':
    action = '1'
  # read the labels file from detect; each line = each bounding box
  #title = stock + ' '+ str(df[-step+5:].index[0].date())+' to '+ str(df[-step+5:].index[-1].date()) + ' (' + str(len(df[-step+5:])) + ' Days)'
  
  with open(save_path + '/exp/labels/' + CHART_TITLE + '.txt') as f:
    lines = f.readlines()
  #store if last 5th candlestick lies between the bounding box
  result = []
  # iterate every bounding box details
  for i in lines:
    #split into [class, x_center, y_center, width, height] and check if class == user desired action
    if i.split()[0] == action:
      x_center = float(i.split()[1])
      width = float(i.split()[3])
      x_right = x_center + (width/2) # normalized x-coordinate to the right
      if x_right >= 0.8125 and x_right <= 0.8515: #only accept bounding box between last 8th(0.8125) to last 3rd(0.8515)candlestick
        result.append(True)
      else:
        result.append(False)
  # Message to user
  st.header('Recommendation:')
  if any(result):
      st.subheader("Suggest to" + user_action + "now.")
  else:
      st.subheader("Suggest to hold.")

######################################################################
############### Plot real 100 days candlestick graph #################
######################################################################
def plot_real_chart(stock, latest_100):    #latest_100 = df[-100:]

  # layout setting of the candlestick graph
  mc = mpf.make_marketcolors(up='#00ff00',down='#ff0000') # green:'#00ff00'; red:'#ff0000'
  s  = mpf.make_mpf_style(base_mpf_style='nightclouds',marketcolors=mc) # set the background to black similar to streamlit

  #title of graph = stock ticker + first day + last day + number of days on the chart
  title = stock + ' '+ str(latest_100.index[0].date())+' to '+ str(latest_100.index[-1].date()) + ' (Past ' + str(len(latest_100)) + ' Days)'

  # plot graph
  fig, ax = mpf.plot(latest_100,type='candle', style=s, ylabel='Price($)', figsize=(20,10),title=title,\
  #need the following in order to return the graph
  returnfig=True)

  st.pyplot(fig)
  st.text("Stock data provided by Yahoo! Finance via yfinance.")

##################################################################################
############################# main function ######################################
##################################################################################


def main():
  ##################################################################################
  ##################################################################################
  ############################# Side Bar User Input ################################
  ##################################################################################
  ##################################################################################

  st.sidebar.title('Buy-Sell Recognition')

  # ask for user_action to buy or sell
  st.sidebar.subheader('Would you like to buy or sell?')
  user_action = st.sidebar.radio('Buy or sell',['buy', 'sell'])

  # ask for stock (what if input not recognized?)
  st.sidebar.subheader('Which stock to ' + user_action + ' now?')
  stock = st.sidebar.text_input('Ticker Symbol', placeholder = 'e.g. TSLA')
  stock = stock.upper()

  # if user would like to sell, ask for his/her buy price for calculation at suggestion stage
  if user_action == 'sell':
      st.sidebar.subheader("Please provide your buy price and loss acceptance.")
      buy_price = st.sidebar.number_input('Buy price', 0.00, 1000000.00, format="%.2f")
      loss_acceptance = st.sidebar.slider('Loss acceptance(%)', 0, 100)

  # button to trigger program run
  st.sidebar.text("") # just for adding white space
  st.sidebar.text("") # just for adding white space

  ##################################################################################
  ############################# Main Page title and warning#########################
  ##################################################################################
  ##################################################################################
  st.image('https://www.constructconnect.com/hubfs/Blog%20Images%20and%20Media/Stock-Markets-Header-Graphic-New-Jan-05-2021-07-18-56-72-PM.jpg')
  st.title('Stock Chart Buy-Sell Recognition')
  st.text('This is a program to suggest if you should buy or sell at the latest stock date.')
  st.text('Input the data on the sidebar.')
  # disclaimer at footer
  footer="""
  <style>
  footer{
  visibility: visible;
  }
  footer:after{
    content: 'The content of this program is not an investment advice\
    and does not constitute any offer or solicitation to offer or recommendation of any investment product.';
    display: block;
    position: center;
    color: grey;
    font-size: 12px;
  }
  </style>
  """
  st.markdown(footer, unsafe_allow_html=True)

  #retrieve data and perform detection only after this button is clicked
  if st.sidebar.button('Check it now!'):
    ##################################################################################
    ##################################################################################
    ############################# Main Page Program ##################################
    ##################################################################################
    ##################################################################################
        
    #this is to check whether the stock exists
    ticker = yf.Ticker(stock)
    info = None
    try:
        info = ticker.info

        # if stock exists, run the program
        st.title(stock)
        # show real time date (by minutes)
        get_now_data(stock)

        #get data from yfinance
        df = get_stock_data(stock,start_date,end_date)

        #plot fake candles chart
        plot_fake_candles_chart(stock,df[-step+5:])
        
        #yolo detection
        run(weights=weight,source=save_path,conf_thres=0.25,save_txt=True,project=save_path)

        #print result
        if user_action == 'sell':
            #stop loss check

            #if stock price is below the stop loss price, recommend selling the stock
            if CURRENT_PRICE < (buy_price - buy_price*loss_acceptance/100):
                #stop loss triggered
                st.header('Recommendation:')
                st.subheader('Current price (' + str(CURRENT_PRICE) + ') below ' +str(loss_acceptance)+ \
                    '% of buy price ('+str(buy_price)+'). It is suggested to sell.')
                
            else:
                #Stop loss not triggered. Give recommendation.
                buy_or_sell(user_action)

        else:
            buy_or_sell(user_action)
        
        # Plot real 100 days candlestick graph    
        plot_real_chart(stock, df[-100:]) 

        #this is to clear the directory that saves the old graph and labels
        #delete the stock chart with fake candles
        os.remove(CHART_TITLE+'.png')
        shutil.rmtree('exp') 

    except:
      st.write("Beep boop! Cannot get info of ",stock,", it probably does not exist.")
    




#run the program

if __name__ == "__main__":
  main()