# Import mplfinance to plot candlestick graph (uncomment if needed)
# pip install mplfinance
# Import yfinance to draw stock data (uncomment if needed)
# pip install yfinance


import os
import shutil
# Import image recognition modules
from detect_save_label import run
# Import streamlit
import streamlit as st

save_path = 'C:/Users/Thomas/Desktop/FTDS bootcamp/Collab Project/yolov5-master/saved'
weight = 'C:/Users/Thomas/Desktop/FTDS bootcamp/Collab Project/best.pt'
#yolo detection
st.write('recognition starts')
run(weights=weight,source=save_path,conf_thres=0.25,save_txt=True)
st.write('recognition done')
