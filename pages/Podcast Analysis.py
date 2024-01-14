#Dashboard com dados da covid no esgoto ETE Serraria

import pandas as pd
import streamlit as st
import plotly.express as px

# Configurações da página
st.set_page_config(
    page_title="UP! Podcast analysis",
    page_icon="	:up:",
    layout="wide",
    initial_sidebar_state='collapsed'
)

# Barra lateral para info
with st.sidebar:
    texto = """
# About the dashboard
This dashboard was created based on a study of the Spotipy library, which facilitates the consumption of the Spotify API. I selected the UP! podcast to evaluate its data and present it in a way that is easy to understand.

# About me
            """
    st.markdown(texto)
    st.image('https://github.com/andrejarenkow/Portfolio/blob/main/imagens_timeline/andre.png?raw=true', width=100)

    texto = """

My name is André Jarenkow, a Python language enthusiast, and a loyal listener to UP!.
            """
    st.markdown(texto)
    


# Título principal do painel
imagem, titulo  = st.columns([1, 6])
titulo.header("Podcast Analysis: UP! - via Spotify API")
titulo.markdown('[Subscribe to UP! starting from BRL 5.00](https://www.catarse.me/up)')
imagem.image('https://i.scdn.co/image/ab6765630000ba8a123f70dfa953d4707a9f2b59', width=100)

#Dados
dados = pd.read_table('https://docs.google.com/spreadsheets/d/e/2PACX-1vTviyi86G1qxhCZacjpN1v8ShugrnPn2Y-WwzcVjpEhNsZCWNcVQAMAOLXwYnj8g_1_IsPx7YMxKr2O/pub?output=tsv',  decimal=',')
dados = dados[['url_imagem','name','release_date', 'description','quem_esta','duration','link_spotify', 'nome_podcast', ]]
dados['duration'] = dados['duration'].astype(float)
dados['quem_esta'] = dados['quem_esta'].str.replace(', ',',')



#Participações
top_participacoes = (dados['quem_esta'].str.get_dummies(',').sum()).reset_index()
top_participacoes.columns = ['Nome', 'Participações']
top_participacoes['Porcentagem'] = top_participacoes['Participações']/len(dados)
top_participacoes['Linha'] = dados['quem_esta'].sort_index(ascending=False).str.get_dummies(',').T.values.tolist()
top_participacoes = top_participacoes.sort_values('Participações', ascending=False)
top_participacoes = top_participacoes.set_index('Nome')

#Métricas
tempo_total = dados['duration'].sum().round(1)

col1, col2, col3 = st.columns(3)
col1.metric("Total episodes", len(dados))
col2.metric("Total time in minutes", tempo_total)
col3.metric("Average time in minutes", dados['duration'].mean().round(1))




#Gráficos
col1, col2, = st.columns([1.5,1])
grafico_duracao = px.scatter(dados, x='release_date', y='duration', color='nome_podcast', hover_data=['name','quem_esta'],
                             color_discrete_sequence=['#FFCB00','purple'],
                             labels={
                     "release_date": "Release date",
                     "duration": "Duration (minutes)",
                     "nome_podcast": "Podcast phase",
                     'name':'Episode name',
                     'quem_esta':'Participants'
                 })
grafico_duracao.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))

with col1:
    st.plotly_chart(grafico_duracao, theme="streamlit", use_container_width=True)

with col2:
    st.markdown('##### Participation Ranking')
    st.dataframe(top_participacoes,
                 column_config={
                    'Nome': st.column_config.Column("Name"),
                    'Participações': st.column_config.Column("Number", width='small'),
                    'Porcentagem': st.column_config.ProgressColumn('Total', help='Percentage of participation in total episodes', min_value=0, max_value=1),
                    'Linha': st.column_config.BarChartColumn('Timeline')
                    })



#Tabela
st.divider()
st.subheader('Episode list')
st.dataframe(dados.set_index('release_date'), 
                column_config={
                    'url_imagem': st.column_config.ImageColumn('Cover', help='Episode Cover', width ='small'),
                    'release_date': st.column_config.DateColumn('Date', format="DD.MM.YYYY", help='Episode release date'),
                    'duration': st.column_config.NumberColumn("Duration (minutes)", format="%d", ),
                    'link_spotify': st.column_config.LinkColumn("Link"),
                    'description': st.column_config.Column("Description"),
                    'quem_esta': st.column_config.Column("Participants"),
                    'name': st.column_config.Column("Episode name")
                    

                })



