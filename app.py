from bs4 import BeautifulSoup
import requests
import time
import datetime as dt 
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import geopandas

import pickle
import os
import streamlit as st

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


all_cities=pickle.load(open('all_cities.pickle','rb'))
city_coordinates=pickle.load(open('city_coordinates.pickle','rb'))
world=geopandas.read_file(r"world-administrative-boundaries (detailed)/world-administrative-boundaries.shp")

default_city_list=['Tbilisi (Georgia)', 'Munich (Germany)', 'Wellington (New Zealand)', 'Santiago (Chile)', 'Miami (Florida)']
#cmap = ['deepskyblue', 'orange','red','olive','purple','aqua','lavender','pink','lawngreen','grey']









def get_temp_graph(city_list):
    df = pd.DataFrame()

    for city, url in all_cities.items():
        if city in city_list:
            city_df = pd.read_html(url)[2]
            city_df = city_df.replace('°F', '', regex=True)
            city_df = city_df.set_index('Average').loc['High'].astype(float)
            city_df=(city_df-32)*5/9 #convert F to C
            city_df = city_df.rename(city)
            df = pd.concat([df, city_df], axis=1)
            
    fig,ax=plt.subplots(figsize=(10,5))
    df.plot.line(ax=ax,marker='o',color=cmap=plt.cm.get_cmap('tab10', len(city_list))[:len(city_list)], fontsize=8)
    ax.set_xticks(range(len(df.index)),df.index)
    ax.set_title('Average Monthly Temperatures By City',fontweight='bold')
    ax.set_ylabel('°C')

    return fig









def default_world_map():
    fig,ax=plt.subplots(figsize=(7,7))
    world.plot(ax=ax,color='lightgrey',ec='black',lw=.1,alpha=0.5)
    ax.scatter(x=[coord['Lon'] for city,coord in city_coordinates.items()],
            y=[coord['Lat'] for city,coord in city_coordinates.items()],
            s=0.2,
            c=[coord['Lat'] if coord['Lat'] is not None and coord['Lat']>=0 else -1*coord['Lat']  if coord['Lat'] is not None else 0 for city,coord in city_coordinates.items()],cmap='hot_r')
    ax.axis('off')








def get_world_graph(city_list):

    lats,lons,cities=[],[],[]
    df = pd.DataFrame()
    for city, url in all_cities.items():
        if city in city_list:
            city_df = pd.read_html(url)[2]
            city_df = city_df.replace('°F', '', regex=True)
            city_df = city_df.set_index('Average').loc['High'].astype(float)
            city_df=(city_df-32)*5/9 #convert F to C
            city_df = city_df.rename(city)
            df = pd.concat([df, city_df], axis=1)

            lats.append(city_coordinates[city]['Lat']), lons.append(city_coordinates[city]['Lon']), cities.append(city)

    fig,ax=plt.subplots(figsize=(10,10))
    world.plot(ax=ax,color='lightgrey',ec='black',lw=.1,alpha=0.6)
    ax.scatter(x=lons,y=lats,s=100,c=cmap=plt.cm.get_cmap('tab10', len(city_list))[:len(cities)])
    for i in range(len(cities)):
        ax.text(lons[i], lats[i],cities[i].split('(')[0].strip(),fontweight='bold',size=6)
    ax.axis('off')

    return fig







#streamlit app

st.set_page_config(layout="wide")
st.header('Comparing Average Monthly Temperatures By City 🌍🌡️- Python Project By Giorgi Beridze')
st.subheader('Visit my [GitHub](https://github.com/beridzeg45) account for code')

selected_cities = st.multiselect(label='Select Cities', options=[''] + [city for city in all_cities], default=default_city_list, label_visibility="hidden")

if selected_cities:
    col1, col2 = st.columns(2)

    with col1: 
        fig_line = get_temp_graph(selected_cities)
        st.pyplot(fig_line)

    with col2:
        fig_world = get_world_graph(selected_cities)
        st.pyplot(fig_world)
else:
    st.write("Please select at least one city to generate the graphs.")
 
