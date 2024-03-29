import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime


# Configurações da página
st.set_page_config(
    page_title="Andre Jarenkow - Portfolio",
    page_icon="	:eyeglasses:",
    layout="wide",
    initial_sidebar_state='expanded'
) 

# Barra lateral para info
with st.sidebar:
    texto = """
# About the dashboard

This dashboard delves into the analysis of traffic accidents in the city of Porto Alegre, Brazil.
It is meticulously constructed using public data generously provided by the municipal government,
allowing users to visualize and map all accidents that have occurred since 2019. 
The dashboard features tailored filters focusing on specific parameters of interest, providing a comprehensive historical overview of accidents. 
Additionally, a unique hexbin map is incorporated to offer an alternative spatial representation of the data, enhancing the depth and versatility of the analysis.


            """
    st.markdown(texto)

st.title('Traffic accidents in Porto Alegre, Brazil')

px.set_mapbox_access_token(st.secrets['MAPBOX_TOKEN'])
#############################################################################
@st.cache_data(ttl='24h')
def load_data():
    acidentes_poa = pd.read_csv('https://dadosabertos.poa.br/dataset/d6cfbe48-ee1f-450f-87f5-9426f6a09328/resource/b56f8123-716a-4893-9348-23945f1ea1b9/download/cat_acidentes.csv', sep=';')
    #puxando diretamente do site, o banco de dados fica sempre atualizado
    acidentes_poa.drop(['data_extracao', 'idacidente' ], axis=1, inplace=True) #limpando o dataframe
    
    acidentes_poa['data'] = pd.to_datetime(acidentes_poa['data']) #passando para formato de data
    acidentes_poa['horario'] = pd.to_datetime(acidentes_poa['hora']).dt.time
    
    acidentes_poa['hora'] = pd.to_datetime(acidentes_poa['hora']).dt.hour
    
    acidentes_poa['ano'] = pd.DatetimeIndex(acidentes_poa['data']).year
    acidentes_poa['mes'] = pd.DatetimeIndex(acidentes_poa['data']).month
    
    acidentes_poa['log1'] = acidentes_poa['log1'].str.strip()
    
    acidentes_poa['log2'] = acidentes_poa['log2'].str.strip()

    acidentes_poa['cruzamento'] = acidentes_poa['log2'].notna()
    
    return acidentes_poa
#############################################################################


col1, col2, col3 = st.columns([1.5,2,2])

#############################################################################
acidentes_poa = load_data()
acidentes_poa = acidentes_poa[acidentes_poa['ano']<2100].reset_index(drop=True)

with col1:
    ano = st.selectbox(
        'Selecione o ano', sorted(acidentes_poa['ano'].unique()), index=3)

df = acidentes_poa.copy()
df = df[(df['latitude']>-31)&(df['latitude']<-29)&(df['longitude']<0)&(df['ano']==ano)]
df['ups_string'] = df['ups'].astype(str)
#############################################################################



#############################################################################
with col1:

    container_filtros = st.container(border=True)
with container_filtros:
    checkbox_cruzamentos = st.toggle('Only traffic intersection', value=False)
    toggle_bicicleta = st.toggle('Only envolving bicycle', value=False)
    
if toggle_bicicleta:
    bicicleta = acidentes_poa['bicicleta']>0
    df = df[bicicleta]


if checkbox_cruzamentos:
    cruzamentos = acidentes_poa['cruzamento']>0
    df = df[cruzamentos]

with col1:
    metric1, metric2, metric3 = st.columns(3)
    metric2.metric('Fatal Accidents' ,len(df[df['ups']==13]))
    metric1.metric('Total Accidents', len(df))
    metric3.metric('Total deaths', df['mortes'].sum()+ df['morte_post'].sum())

#############################################################################
with col2:

    tab_scatter, tab_mapa_calor = st.tabs([ 'Scattermap','Hexbin map'])
    
with tab_mapa_calor:
    fig = ff.create_hexbin_mapbox(
        data_frame=df, lat="latitude", lon="longitude",
        nx_hexagon=30, opacity=0.6, labels={"color": "Accidents"}, zoom=10, min_count=1, color_continuous_scale="Magma_r", title='Hexbin map', height=600
    
    )
    fig.update_layout(margin=dict(b=0, t=0, l=0, r=0))
    fig.update_layout( mapbox_style="open-street-map")   
    
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',margin=go.layout.Margin(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

with tab_scatter:
    scatter_fig = px.scatter_mapbox(df.sort_values('ups'), lat = 'latitude', lon = 'longitude',
                                    zoom = 9.5,
                                    mapbox_style = 'open-street-map',
                                    color_discrete_sequence = ['blue','gold','darkred'],
                                    color = 'ups_string',
                                    size='ups',
                                    opacity = 0.4,
                                    center=dict(lat=-30.085815797161448 , lon= -51.17306247847506),
                                    hover_name="log1",
                                    hover_data= ['data','horario', 'tipo_acid', 'dia_sem'],
                                    title = 'Traffic Accidents by Standard Severity Unity',
                                    labels={'ups_string':'Severity'},
                                    height=600)
    
    
    scatter_fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', margin=go.layout.Margin(l=10, r=30, t=30, b=10),)
    st.plotly_chart(scatter_fig, use_container_width=True)
    

top10 = pd.pivot_table(data = df, index='log1', columns='ups', aggfunc='count', values='noite_dia').fillna(0)
top10.columns = ['Light','Medium', 'Severe']
top10['Total'] = top10.sum(axis=1)
top10['Fatal %'] = top10['Severe']/top10['Total']*100
top10 = top10.rename_axis('Street name')


with col1:
    st.dataframe(top10.sort_values('Severe', ascending=False))

#########################
#acidentes por hora do dia
acidentes_poa_hora = pd.pivot_table(df, index=['hora'],aggfunc='count', columns=['dia_sem'], values=['tipo_acid']).reset_index()
acidentes_poa_hora.columns = acidentes_poa_hora.columns.droplevel()
acidentes_poa_hora = acidentes_poa_hora[['', 'DOMINGO','SEGUNDA-FEIRA', 'TERÇA-FEIRA', 'QUARTA-FEIRA',
                                         'QUINTA-FEIRA', 'SEXTA-FEIRA', 'SÁBADO']]

acidentes_poa_hora.columns = ['hora', 'Sunday','Monday', 'Tuesday', 'Wednesday',
                                         'Thursday', 'Friday', 'Saturday']


acidentes_poa_hora['hora'] = acidentes_poa_hora['hora'].map('{:,.0f}'.format)

hora = []

for i in acidentes_poa_hora['hora']:
  hora.append(str(i) + ':00')
acidentes_poa_hora['hora'] = hora

acidentes_poa_hora.set_index('hora', inplace=True)



acid_hora = px.imshow(acidentes_poa_hora, text_auto=True, aspect='auto', labels=dict(x="Day of Week", y="Time of Day", color="Accidents", color_continuous_scale = 'Reds'))


#########################
if toggle_bicicleta:
    bicicleta = acidentes_poa['bicicleta']>0
    df_graf_lin = acidentes_poa[bicicleta]

else:
    df_graf_lin = acidentes_poa
acidentes_por_mes = df_graf_lin['data'].dt.to_period('M').value_counts().reset_index()
acidentes_por_mes.columns=['date', 'accidents']
acidentes_por_mes = acidentes_por_mes[acidentes_por_mes['date']<'01-01-2100'].sort_values('date')
acidentes_por_mes['date'] = acidentes_por_mes['date'].astype(str)
acid_mes = px.line(acidentes_por_mes, x='date', y='accidents', title='Accidents per month', markers=True)
acid_mes.update_layout(yaxis_range=[0,acidentes_por_mes['accidents'].max()*1.1])
##########################

with col3:
    st.plotly_chart(acid_mes, use_container_width=True)
    #st.plotly_chart(acid_hora, theme=None)
    st.markdown("[Data source](https://dadosabertos.poa.br/dataset/acidentes-de-transito-acidentes)")
    st.markdown('Map legend: 1 - Accidents with only material damage; 5 - Accidents with people injured; 13 - Accidents with fatal victms')






