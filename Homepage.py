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
from streamlit_lottie import st_lottie
 
# Configurações da página
st.set_page_config(
    page_title="Andre Jarenkow - Portfolio",
    page_icon="	:bug:",
    layout="wide",
    initial_sidebar_state='collapsed'
) 

# Função Lottie
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


# Barra lateral para info
with st.sidebar:
 
    st.image('https://github.com/andrejarenkow/Portfolio/blob/main/imagens_timeline/andre.png?raw=true')
    texto = """
Hello! My name is André Jarenkow, and this is my Portfolio!.
            """
    st.markdown(texto)
    st_lottie('https://raw.githubusercontent.com/andrejarenkow/Portfolio/main/Animation%20-%201705284418621.json')



    


st.title('Portfolio André Jarenkow')

career_timeline = st.container(border=True)
with career_timeline:
 st.subheader('Career timeline')
 with st.spinner(text="Building line"):
     with open('timeline.json', "r") as f:
         data = f.read()
         timeline(data, height=500)
