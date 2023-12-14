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
from streamlit_timeline import timeline
 
# Configurações da página
st.set_page_config(
    page_title="Andre Jarenkow",
    page_icon="	:bug:",
    layout="wide",
    initial_sidebar_state='collapsed'
) 

# Barra lateral para info
with st.sidebar:
    texto = """
# Sobre o painel
Este painel foi feito a partir de um estudo da biblioteca Spotipy, a qual facilita o consumo da API do Spotify. Selecionei o podcast UP! para avaliar seus dados, e deixá-los postos de uma maneira
que fosse fácil de entender.

# Sobre mim
            """
    st.markdown(texto)
    st.image('https://media.licdn.com/dms/image/D4D03AQEDuEud7TtpUw/profile-displayphoto-shrink_800_800/0/1664902362993?e=1704326400&v=beta&t=-FzZf4tS3p9l4KsfqoCMUAGDiaMUkmLcTHb6d6-UczA', width=100)

    texto = """

Me chamo André Jarenkow, entusiasta da linguagem Python e ouvinte fiel ao UP!.
            """
    st.markdown(texto)


st.title('Portfolio André Jarenkow')

st.subheader('Career timeline')
with st.spinner(text="Building line"):
    with open('timeline.json', "r") as f:
        data = f.read()
        timeline(data, height=500)
