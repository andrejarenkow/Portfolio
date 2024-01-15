import pandas as pd
import geopandas as gpd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium, folium_static

# Configurações da página
st.set_page_config(
    page_title="Andre Jarenkow - Portfolio",
    page_icon="	:eyeglasses:",
    layout="wide",
    initial_sidebar_state='expanded'
) 
col1, col2, col3 = st.columns([1,4,1])

col1.image('https://github.com/andrejarenkow/PainelOvitrampas/blob/main/logo_cevs%20(1).png?raw=true', width=200)
col2.title('Antivenom Locator in Rio Grande do Sul')
col3.image('https://github.com/andrejarenkow/PainelOvitrampas/blob/main/logo_estado%20(3).png?raw=true', width=300)

# Barra lateral para info
with st.sidebar:
    texto = """
# About the webapp
This web app was created to locate antivenom in case of accidents involving venomous animals in the state of Rio Grande do Sul, in southern Brazil. 
The methodology tab provides a detailed description of how the database, which enables the web app's functionality, was generated.
It has become an official tool for the state. 
This was a team effort, developed under my supervision.

            """
    st.markdown(texto)

tab1, tab2, tab3 = st.tabs(["Antivenom Locator App", "About", "Methodology"])
                           
with tab1:
    st.header("Antivenom Locator")
    #dicionario soros
    dicionario_explicacao = {
        "SAB - Soro antibotrópico - jararacas, cruzeira, cotiara" : ": This antidote is used for the treatment of snakebites by snakes of the Bothrops genus. In Rio Grande do Sul, we find: Bothrops jararaca (jararaca), Bothrops pubescens (painted jararaca), Bothrops alternatus (cruzeira), Bothrops diporus (painted jararaca), and Bothrops cotiara (cotiara).",
        "SAC - Soro anticrotálico - cascavel" : ": This antidote is used for the treatment of snakebites by snakes of the Crotalus genus. In Rio Grande do Sul, we have Crotalus durissus (rattlesnake).",
        "SAEl - Soro antielapídico - coral verdadeira" : ": This antidote is used for the treatment of snakebites by snakes of the Micrurus genus. In Rio Grande do Sul, we find Micrurus altirostris (true coral snake).",
        "SAEsc - Soro antiescorpiônico - escorpião amarelo" : ": This antidote is used for the treatment of envenomation by scorpions of the Tityus genus. In Rio Grande do Sul, it is mainly used for the treatment of envenomation by Tityus serrulatus (yellow scorpion).",
        "SAAr - Soro antiaracnídico - armadeira, marrom" : ": This antidote is used for the treatment of envenomation by spiders of the Phoneutria genus (wandering spider), Loxosceles genus (brown recluse), and scorpions of the Tityus genus.",
        "SALon - Soro antilonômico - taturana" : ": This antidote is used for the treatment of envenomation by caterpillars of the Lonomia genus (caterpillar)."
    }
    
    dicionario = {"Restinga Seca": "Restinga Sêca",
        "Santana do Livramento": "Sant'Ana do Livramento","Santo Antônio Das Missões":"Santo Antônio das Missões", "São Pedro Das Missões":"São Pedro das Missões"}
    
    
    dados_geral = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vTeWn7SmYQbdwulQtkslW2OeNEV-XGEPVcAnlUI1QnnstfjxpUgHgSl3cOrUsX0qlJ6Q9Ef7MvPAUOf/pub?gid=669334724&single=true&output=csv')
    dados_geral['Latitude_origem']=pd.to_numeric(dados_geral['Latitude_origem'].str.replace(',','.'))
    dados_geral['Longitude_origem']=pd.to_numeric(dados_geral['Longitude_origem'].str.replace(',','.'))
    dados_geral['Latitude_destino']=pd.to_numeric(dados_geral['Latitude_destino'].str.replace(',','.'))
    dados_geral['Longitude_destino']=pd.to_numeric(dados_geral['Longitude_destino'].str.replace(',','.'))
    
    municipios = gpd.read_file('https://raw.githubusercontent.com/andrejarenkow/geodata/main/municipios_rs_CRS/RS_Municipios_2021.json')
    municipios['geometry'] = municipios['geometry'].simplify(tolerance = 0.01)
    municipios["NM_MUN"] = municipios["NM_MUN"].replace(dicionario)
    
    lista_mun_distinct = sorted(municipios['NM_MUN'].unique())

    col5, col4 = st.columns([3, 4]) 
    with col5:  
        animal = st.selectbox("What type of animal caused the incident?", dados_geral['Animal'].unique(), index=None, placeholder="Select the animal")
        soro = st.selectbox('Antivenom', dados_geral[dados_geral['Animal']==animal]['soro'].unique(), index=None, placeholder="Select the antivenom")
            
        try: 
            container = st.container(border=True)
            with container: 
             st.write(soro, dicionario_explicacao[soro])
        except: 
            st.write("")
    
        mun_origem = st.selectbox('Municipality where the patient is located', lista_mun_distinct, index=None, placeholder="Select the municipality")
        #if mun_origem==municipio_do_usuario:
           # mun_origem = municipio_do_usuario
        try:
            
            #Filtro destino
            filtro = (dados_geral['soro'] == soro)&(dados_geral['Origin'] == mun_origem)
            municipio_origem = dados_geral[filtro]
            municipio_origem['Legenda'] = 'Origem'
            
            #municipio_origem = municipio_origem.reset_index(drop=True)
            mun_destino = municipio_origem.dropna()['Município destino'].values[0]
                
            filtro_destino = (dados_geral['soro'] == soro)&(dados_geral['Origin'] == mun_destino)
            municipio_destino = dados_geral[filtro_destino].dropna()
            municipio_destino['Legenda'] = 'Destino'
        
            latitude_media = (municipio_origem['Latitude_origem'].values + municipio_destino['Latitude_destino'].values)/2
            longitude_media = (municipio_origem['Longitude_origem'].values + municipio_destino['Longitude_destino'].values)/2
           
            mapa = folium.Map([latitude_media,  longitude_media], zoom_start=9)
        
            folium.Marker(
                location= [municipio_origem['Latitude_origem'].values, municipio_origem['Longitude_origem'].values],
                tooltip="Origin",
                popup="You are here",
                icon=folium.Icon(color="green"),
            ).add_to(mapa)
            
            folium.Marker(
                location= [municipio_destino['Latitude_destino'].values, municipio_destino['Longitude_destino'].values],
                tooltip="Destiny",
                popup=f"The antivenom is here, in {municipio_destino['Município destino'].values[0]}, {municipio_destino['Destination'].values[0]}",
                icon=folium.Icon(color="red"),
             ).add_to(mapa)
            
            #folium.TileLayer('MapQuest Open Aerial').add_to(mapa)
        
            with col4: 
                st.subheader('Nearest hospital')
                st_data = folium_static(mapa, width=1000, height=600)
            with col5:
                mun_destino = municipio_origem.dropna()['Município destino'].values[0]
                distancia = municipio_origem.dropna()['shortest way (km)'].values[0]
                local = municipio_origem.dropna()['Destination'].values[0]
                endereco = municipio_origem.dropna()['Endereço'].values[0]
                telefone = municipio_origem.dropna()['Telefone'].values[0]
                container_respostas = st.container(border=True)
                with container_respostas: 
                    st.write(f'Município onde está o soro mais próximo: **{mun_destino}**')
                    st.write(f'Local: **{local}**')
                    st.write(f'Endereço: **{endereco}**')
                    st.write(f'Telefone: **{telefone}**')
                    st.write(f'Distância: **{distancia} km**')
                    st.write('**ATENÇÃO**: ligue para o local para fazer a confirmação da disponibilidade do soro.')
        except:
            with col4:
                if soro:
                    filtro = (dados_geral['soro'] == soro)&(dados_geral['Animal'] == animal)
                    dados_mapa_vazio = dados_geral[filtro]
                
                elif animal:
                    filtro = (dados_geral['Animal'] == animal)
                    dados_mapa_vazio = dados_geral[filtro] 
      
                else:
                    dados_mapa_vazio = dados_geral.copy()
                
                pontos = dados_mapa_vazio.drop_duplicates(['Destination'])
          
                mapa_vazio = folium.Map([-29.492046590850748, -53.10367543293593], zoom_start=6.3)
                
                for latitude, longitude, hospital, endereco  in zip(pontos['Latitude_destino'], pontos['Longitude_destino'], pontos['Destination'], pontos['Endereço']):
                    folium.Marker(
                        location= [latitude, longitude],
                        tooltip=hospital,
                        popup=endereco,
                        icon=folium.Icon(color="red"),
                    ).add_to(mapa_vazio)
                st.subheader('Todos os hospitais')
                st_data = folium_static(mapa_vazio, width=1000, height=600)

with tab2:
    st.header("Types of accident")
    texto_sobre_ofidicos =     """
    ### SNAKEBITES
    
B Bothropic accidents are those caused by snakes of the genus _Bothrops_ sp., with the most common being the jararaca (_Bothrops jararaca_), the cruzeira (_Bothrops alternatus_), and the painted jararaca (_Bothrops pubescens_).
Occasionally, accidents may occur with two rarer species, the _Bothrops diporus_ and the _Bothrops cotiara_.
Crotalic accidents are those caused by the rattlesnake (_Crotalus durissus_). In Rio Grande do Sul, elapidic accidents are primarily caused by _Micrurus altirostris_, one of several species of true corals found in Brazil, and distributed throughout the state.
    """

    st.markdown(texto_sobre_ofidicos)
    
    texto_bothrops_cotiara = """
    **_Bothrops cotiara_**: Cotiara, black-bellied jararaca, black jararaca. It has a brownish-green coloration with trapezoid patterns.
    The belly is black. Average length is around 80 cm. Nocturnal activity. 
    A terrestrial snake with low population density, it is distributed in the northern part of the state, in the Araucaria forest areas - an ecosystem that has been significantly reduced.
    As a result, cotiara is threatened with extinction in Rio Grande do Sul. It feeds exclusively on small rodents and marsupials. Its venom has proteolytic, coagulant, and hemorrhagic actions.
    """
    imagem_bothrops_cotiara = 'https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/BCotiara_1.jpg?raw=true'
    
    bothrops_cotiara_container = st.container(border=True)
    with bothrops_cotiara_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_bothrops_cotiara)
        imagem.image(imagem_bothrops_cotiara, width=500)
    
    
    
    texto_bothrops_diporus = """
    **_Bothrops diporus_**: Painted jararaca, Argentine painted jararaca. Brown with trapezoid-shaped patterns. Spotted belly, similar to _B. pubescens_. Can measure up to 1 m. Crepuscular and nocturnal activity. Common in forests and plantations. Highly adapted to environments modified by humans. Venom has proteolytic, coagulant, and hemorrhagic actions.

    """
    bothrops_diporus_container = st.container(border=True)
    with bothrops_diporus_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_bothrops_diporus)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/Bothrops_diporus_2.jpg?raw=true', width=500)    
       
    
    
    texto_bothrops_jararaca =  """
    **_Bothrops jararaca_**: Jararaca, common jararaca. Brownish-green, with dark patterns in the shape of an inverted V. Averages 1 m in length. Crepuscular and nocturnal activity. Common in forests, especially in remnants of the Atlantic Forest. Semi-arboreal. Venom has proteolytic, coagulant, and hemorrhagic actions.
"""
    bothrops_jararaca_container = st.container(border=True)
    with bothrops_jararaca_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_bothrops_jararaca)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/BJararaca_3.jpg?raw=true', width=500)        
 
    texto_bothrops_alternatus = """
    **_Bothrops alternatus_**: Cruzeira, urutu, urutu-cruzeira, cross urutu, vibora de la cruz. Tan or greenish-brown with horseshoe or white-edged telephone hook patterns. Has brownish spots on the belly. On the head, it has a clear cross-shaped pattern on a dark background. Measures between 1 and 1.5 m. It is the largest and most robust among the _Bothrops_ sp. in the state. Crepuscular and nocturnal activity. A more robust snake, found in open areas. Lives in humid places with low vegetation. It usually enters forests or plantations to feed exclusively on small rodents and marsupials. Venom has proteolytic, coagulant, and hemorrhagic actions.
"""
    bothrops_alternatus_container = st.container(border=True)
    with bothrops_alternatus_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_bothrops_alternatus)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/Balternathus_4.jpg?raw=true', width=500) 

    
    texto_bothrops_pubescens = """
    **_Bothrops pubescens_**: Painted jararaca, white-tailed jararaca, Uruguayan painted jararaca, Pampas jararaca. Brown with trapezoid-shaped patterns. Spotted belly. Averages around 60 cm. Crepuscular and nocturnal activity. A common species in open fields, such as the Pampas biome, and may enter plantations. It is smaller and quite reactive. Venom has proteolytic, coagulant, and hemorrhagic actions.
    """
    bothrops_pubescens_container = st.container(border=True)
    with bothrops_pubescens_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_bothrops_pubescens)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/B-pubescens_5.jpg?raw=true', width=500)     

    texto_crotalus_durissus = """
    **_Crotalus durissus_**: Rattlesnake. Yellowish-brown with lighter diamond-shaped patterns on the back and sides. Measures up to 1.5 m. Active during the afternoon and night, mainly at dusk. Lives in high, mountainous, rocky areas with interspersed fields and cold winters. It has a crepitacle (rattle) of horny rings at the tip of the tail that, when moved during stressful moments, emits the sound of the rings clashing. It rarely attacks and announces its presence through the rattling sound. Hunts by ambush - remains still on the ground, waiting for the prey (rodent) to pass. Venom has neurotoxic, myotoxic, and coagulant actions.
    """
    crotalus_durissus_container = st.container(border=True)
    with crotalus_durissus_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_crotalus_durissus)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/Crotalus_durissus_6.jpg?raw=true', width=500)   
    

    texto_micrurus_altirostris = """
    **_Micrurus altirostris_**: True Coral Snake. This species is characterized by the presence of black and white rings on a red background, encircling the entire body. It measures up to 80 cm. Activity primarily occurs during the day, reducing towards the night. True coral snakes have fossorial habits, living in burrows or holes under the ground in forests or forest edges. They do not have specialized fangs like Viperidae but small teeth. They need to bite and hold the prey to inject the venom. They feed on other snakes. Venom has neurotoxic action.
    """
    micrurus_altirostris_container = st.container(border=True)
    with micrurus_altirostris_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_micrurus_altirostris)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/M-altirostris_7.jpg?raw=true', width=500) 
        
    st.divider()
    texto_sobre_aranhas = """
    ### SPIDER BITES
    
    Spider poisonings predominate in Rio Grande do Sul compared to other accidents involving venomous animals. There are two species of spiders of medical importance in the state, whose poisonings can be treated with antivenom: _Loxosceles intermedia_, the brown recluse spider, and _Phoneutria nigriventris_, the wandering spider.
    """
    st.markdown(texto_sobre_aranhas)

    texto_loxosceles = """
    **_Loxosceles intermedia_**: The brown recluse spider is characteristic of urban centers and can remain inside residences, hidden behind furniture, and sometimes amidst personal clothing, bedding, and towels. Accidents occur when the patient accidentally crushes the Loxosceles against their own body while dressing, putting on shoes, or cleaning the house. It is not an aggressive spider and is quite small. The accident can lead to the appearance of areas of ischemia and necrosis in the skin, requiring tissue debridement. There may be a loss of large muscle areas.
    """
    loxosceles_container = st.container(border=True)
    with loxosceles_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_loxosceles)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/thumbnail_Loxosceles%20-%20aranha-marrom_8.jpg?raw=true', width=500) 
    
    texto_phoneutria = """
    **_Phoneutria nigriventris_**: The wandering spider is a larger arachnid and exhibits reactive behavior – when feeling threatened, it can jump on a person or animal, causing the accident. The wandering spider is more common in rural areas and can enter sheds, basements, and even homes during the reproductive period, between March and May, when males become wanderers in search of females. The accident causes intense pain.
    """
    phoneutria_container = st.container(border=True)
    with phoneutria_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_phoneutria)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/Phoneutria%20-%20armadeira_9.jpeg?raw=true', width=300) 

    texto_sobre_escorpiao = """
    ### SCORPION ACCIDENTS
    
    In Rio Grande do Sul, there are several species of scorpions, with the majority being of low toxicity. However, _Tityus serrulatus_, popularly known as the yellow scorpion, is responsible for high toxicity accidents and, in some cases, requires treatment with scorpion antivenom or antiscorpion venom.
    """
    st.divider()
    st.markdown(texto_sobre_escorpiao)
    

    texto_tityus = """
    **_Tityus serrulatus_**: The yellow scorpion is exotic to the state, native to Minas Gerais, and it is likely that it has spread throughout Brazil through human road transport, often hidden in products like vegetables and fruits. Upon arriving in new locations, if there is food (especially cockroaches), water, and shelter, _T. serrulatus_ quickly adapts and multiplies, becoming endemic. The main groups at risk for yellow scorpion accidents are children and the elderly. It reaches a maximum size of 7 cm. It has a yellow body with darker details on the dorsum, pincers, and tail tip. It can also be identified by the serrations on the tail. The venom of the yellow scorpion can cause changes in heart rate, respiratory rate, and blood pressure.
    """
    tityus_container = st.container(border=True)
    with tityus_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_tityus)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/Tiyus_serrulatus_10.jpg?raw=true', width=500)     

    texto_lagarta = """
    ### LARVAE ACCIDENTS
    
    There are several urticating caterpillars in Rio Grande do Sul, but _Lonomia obliqua_, known as the "taturana," is the only one that can cause severe accidents requiring the use of antilonomic serum.
    """
    st.divider()
    st.markdown(texto_lagarta)
    
    texto_lonomia = """
    **_Lonomia obliqua_**: Known as the "taturana," its life cycle lasts, on average, 150 days. The caterpillar phase, which poses a danger due to the presence of urticating bristles, lasts for 60 days. During this phase of life, the caterpillars remain clustered on tree trunks during the day and, at night, climb to the treetops to feed on leaves. Due to their tendency to stay clustered, when an accident occurs, the patient comes into contact with several individuals simultaneously. The major danger of this accident is its toxin, which can lead to acute renal failure.
    """
    lonomia_container = st.container(border=True)
    with lonomia_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_lonomia)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/Taturana-11.jpg?raw=true', width=500)       
    


    
    
with tab3:
    st.header("Metodologia")
    texto_metodologia_1 = """    
        
**Methodology for Creating the "Antivenom Locator"**

The methodology used for gathering information to create the "Antivenom Locator" was developed in the QGIS software, utilizing a process called Network Analysis. The objective was to obtain the distances from the municipalities in Rio Grande do Sul to the nearest antivenom focal point. The project was conceptualized using shapefile data (lines, points, and polygons), tools, and plugins from the QGIS program.

Initially, the Antivenom Focal Points (locations where antivenoms are available) were introduced and spatialized in the software, allowing for their visualization on the territory of the state of Rio Grande do Sul. These Focal Points were obtained through a table provided by the Toxicological Information Center (CIT). Alongside the Focal Points, points of the municipal headquarters of Rio Grande do Sul were added (these points were identified from the urban centers of the municipalities), a shapefile of RS highways, and a shapefile of RS state polygons (Figure 1).

![Figure 1](https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/figura1.png?raw=true "Figure 1")

Antivenom Focal Points in red. Municipal Headquarters in blue. RS Highways in brown.

Once all the data was organized, the Network Analysis was conducted using tools and plugins in QGIS. A geoprocessing of the data was performed to obtain the distances from the municipal headquarters to the Antivenom Focal Points. The geoprocessing was based on the QNEAT3 plugin, which created straight-line distances from the Focal Points to the municipal headquarters of the state. As the primary means of transportation for the population is by car, a correction of the distances was made using the state highway network (Figure 2).

![Figure 2](https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/figura4%20certa.png?raw=true "Figure 2")

Network Analysis geoprocessing performed for Focal Points with Antivenom SAB. In green, the distance from the municipal headquarters of each municipality in RS to the nearest Focal Point, based on the state highways.

Since not all Focal Points have all six available Antivenoms in their stock, the geoprocessing was performed six times, once for each Antivenom. Once for Focal Points with SAB, once for Focal Points with SAC, and so on (Figure 3).
    """
    
    
    
    
    texto_metodologia_2 =  """
    
**Antivenom Types:**
1. Antivenom SAC
2. Antivenom SAE
3. Antivenom Saar
4. Antivenom SAEsc
5. Antivenom SAB
6. Antivenom SALon

As a final product of the applied methodology, tables were obtained for the municipalities of Rio Grande do Sul, indicating which Focal Point is closest to each municipality, along with the corresponding distance in kilometers. A separate table was generated for each Antivenom (SAB, SAC, SAE, SAEsc, SALon, and Saar) (Figure 4).

![Figure 4](https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/figura4.png?raw=true "Figure 4")

Example table generated after geoprocessing of the data. Table for Antivenom SAB.

#### Methodological Flow

![Methodological Flow](https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/fluxo%20metodologico.png?raw=true "Methodological Flow")  
    """

    st.markdown(texto_metodologia_1)
    st.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/figura3.png?raw=true', width=1200 )
    st.markdown(texto_metodologia_2)

creditos = st.container(border=True)
with creditos:
    st.write('Application developed by the team of the Division of Environmental Surveillance in Health of the State Center for Health Surveillance of the State Health Department of Rio Grande do Sul.')
    st.write('Members: Bárbara Mendes Pietoso, Carlo Johannes Lipp Nissinen, Carolina Schell Franceschina e André Jarenkow')
           
