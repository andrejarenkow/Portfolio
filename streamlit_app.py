#Importação das bibliotecas 
import requests
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium, folium_static
import streamlit as st
import time
from altair import Chart
import plotly.figure_factory as ff
import geopandas as gpd
 
# Configurações da página
st.set_page_config(
    page_title="Andre Jarenkow",
    page_icon="	:bug:",
    layout="wide",
    initial_sidebar_state='collapsed'
) 

with st.spinner(text="Building line"):
    with open('timeline.json', "r") as f:
        data = f.read()
        timeline(data, height=500)


st.title('Portfolio André Jarenkow')
