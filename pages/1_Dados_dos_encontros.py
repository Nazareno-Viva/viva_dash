import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import plotly.graph_objects as go

st.title("Dados dos encontros")


# Dado grupos 
grupos = "https://docs.google.com/spreadsheets/d/\
1gzSyaOKJMTedbg3ruPC-EZj3kP1iE4xU2Xn4UclxjLM/export?format=csv"

encontros = "https://docs.google.com/spreadsheets/d/\
17uIz_Lc_3nwRTtDI7x4G96AcZ16ac-t3FAUahnanUSY/export?format=csv"

participantes = "https://docs.google.com/spreadsheets/d/\
1-a9IiR54ex43F5HOmYQyFPvxybFFi6SQSiF79Ztb3wg/export?format=csv"

de = pd.read_csv(encontros)         
dg = pd.read_csv(grupos) 

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

# Adicional filtros
categorias = st.sidebar.multiselect(
    "Selecione o líder:",
    options=dge['Nome do Lider'].unique(),
    default=dge['Nome do Lider'].unique()
)

# Filtro por intervalo de datas
data_inicial = st.sidebar.date_input("Data inicial", dge['Data'].min())
data_final = st.sidebar.date_input("Data final", dge['Data'].max())

# --- Aplicando filtros ---
df_filtrado = dge[
    (dge['Nome do Lider'].isin(categorias)) &
    (dge['Data'] >= pd.to_datetime(data_inicial)) &
    (dge['Data'] <= pd.to_datetime(data_final))
]

df_filtrado['Data Formatada'] = df_filtrado['Data'].dt.strftime('%d/%m/%Y')
df_filtrado.drop_duplicates(inplace=True)
df_filtrado.reset_index(drop=True, inplace=True)
df_filtrado = df_filtrado.sort_values(by='Data')

df_filtrado.rename(columns={'Nome do Lider':'Líder',
                    'Número de participantes':'Frequência',
                    'Data Formatada':'Datas'
                    }, inplace=True)

fig = go.Figure(data=[
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


fig.update_layout(
    xaxis_tickformat="%d/%m/%Y",
)

col11, col12 = st.columns([7, 3])

with col11:
    st.subheader("Gráfico de frequência")
    st.plotly_chart(fig, use_container_width=True)

with col12:
    st.subheader("Gráfico")
    st.dataframe(df_filtrado[['Líder', 
                              'Datas', 
                              'Frequência'
        ]], use_container_width=True)



# with col11:
#     st.subheader("Tabela de Dados")
#     st.dataframe(df_filtrado)

# # Gráfico na segunda coluna
# with col12:
#     st.subheader("Gráfico de Barras")
#     fig, ax = plt.subplots()
#     ax.bar(df['Categoria'], df['Valores'])
#     st.pyplot(fig)
