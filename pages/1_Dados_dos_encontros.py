import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
load_dotenv()

st.title("Dados dos encontros")
 

dg = pd.read_csv(os.environ["GRUPO"])         
de = pd.read_csv(os.environ["ENCONTROS"]) 


de.drop_duplicates(inplace=True)
de['Data'] = pd.to_datetime(de['Data da reunião'], format="%d/%m/%Y")
de.drop(['Nome do Líder'], axis=1, inplace=True)

dge = pd.merge(de, dg[['Nome do Lider', 'Identificador do grupo']], 
               how='inner', 
               on=['Identificador do grupo'])

dge['Nome do Lider'] = dge['Nome do Lider'].str.strip()

_colunas = [
    'Número de participantes', 
    'Número de visitantes', 
    'Data',
    'Nome do Lider'
]

dge = dge[_colunas].copy()
dge.sort_values(by='Data')
dge.drop_duplicates(inplace=True)
dge.reset_index(drop=True, inplace=True)

df = pd.DataFrame()

for _lider in dge['Nome do Lider'].unique():
    dftemp = dge[dge['Nome do Lider'] == _lider].copy()
    dftemp.sort_values('Data', inplace=True)
    dftemp['Data inicial'] = dftemp['Data'].shift(1)
    dftemp['Data inicial'] = dftemp['Data inicial'].fillna(dftemp['Data'].min())
    dftemp['Dias'] = (dftemp['Data']-dftemp['Data inicial']).dt.days

    df = pd.concat([df, dftemp])



# Adicional filtros
categorias = st.sidebar.multiselect(
    "Líder:",
    options=dge['Nome do Lider'].unique(),
    default=dge['Nome do Lider'].unique()
)

# Filtro por intervalo de datas
data_inicial = st.sidebar.date_input("Data inicial", dge['Data'].min())
data_final = st.sidebar.date_input("Data final", dge['Data'].max())

# --- Aplicando filtros ---
df_filtrado = df[
    (df['Nome do Lider'].isin(categorias)) &
    (df['Data'] >= pd.to_datetime(data_inicial)) &
    (df['Data'] <= pd.to_datetime(data_final))
]

df_filtrado['Data Formatada'] = df_filtrado['Data'].dt.strftime('%d/%m/%Y')
df_filtrado.drop_duplicates(inplace=True)
df_filtrado.reset_index(drop=True, inplace=True)
df_filtrado = df_filtrado.sort_values(by='Data')

df_filtrado.rename(columns={'Nome do Lider':'Líder',
                    'Número de participantes':'Frequência',
                    'Data Formatada':'Datas'
                    }, inplace=True)

fig1 = go.Figure(data=[
    go.Scatter(
        name=_nome,
        mode='lines+markers+text',
        x=df_filtrado[df_filtrado['Líder'] == _nome]['Data'],
        y=df_filtrado[df_filtrado['Líder'] == _nome]['Frequência'],
        text=df_filtrado[df_filtrado['Líder'] == _nome]['Frequência'],
        textposition='top center', 
        marker=dict(size=10),
        line=dict(width=2)  
    )
    for _nome in df_filtrado['Líder'].unique()
])


fig1.update_layout(
    xaxis_tickformat="%d/%m/%Y",
)

fig2 = go.Figure(data=[
    go.Scatter(
        name=_nome,
         mode='lines+markers+text',
        x=df_filtrado[(df_filtrado['Líder'] == _nome) & (df_filtrado['Dias']>0)]['Data'],
        y=df_filtrado[(df_filtrado['Líder'] == _nome) & (df_filtrado['Dias']>0)]['Dias'],
        text=df_filtrado[(df_filtrado['Líder'] == _nome) & (df_filtrado['Dias']>0)]['Dias'],
        textposition='top center', 
        marker=dict(size=10),
        line=dict(width=2)  
    )
    for _nome in df_filtrado['Líder'].unique()
])


fig2.update_layout(
    xaxis_tickformat="%d/%m/%Y",
)

col11, col12 = st.columns([7, 3])

with col11:
    st.subheader("Gráfico de frequência")
    st.plotly_chart(fig1, use_container_width=True)

with col12:
    st.subheader("Gráfico")
    st.dataframe(df_filtrado[['Líder', 
                              'Datas', 
                              'Frequência'
        ]], use_container_width=True)

col21, col22 = st.columns([7, 3])

with col21:
    st.subheader("Gráfico de dias entre os encontros")
    st.plotly_chart(fig2, use_container_width=True)

with col22:
    st.subheader("Gráfico")
    st.dataframe(df_filtrado[df_filtrado['Dias']>0][['Líder', 
                              'Datas', 
                              'Dias'
        ]], use_container_width=True)




