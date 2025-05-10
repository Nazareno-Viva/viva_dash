import pandas as pd
import plotly.express as px
import locale
import os
import streamlit as st

from dotenv import load_dotenv
load_dotenv()


st.title("Novos decididos")

df = pd.read_csv(os.environ["NDS"])   

_colunas = ['Idade', 
            'Estado Civil',
            'Qual a sua decisão hoje?',
            'Data da decisão', 
            'A decisão ocorreu em qual culto?',
            'Você é batizado nas águas em alguma igreja Evangélica?',
            'Como chegou à VIVA?']


_coluna_rename = {'Qual a sua decisão hoje?':'Decisão',
                  'Data da decisão':'Data',
                  'A decisão ocorreu em qual culto?':'Período do culto',
                  'Você é batizado nas águas em alguma igreja Evangélica?':'Batizado',
                  'Como chegou à VIVA?':'Forma de convite'}

_idade_ordem = {'30 - 40 anos':5, 
                '> 40 anos':6,  
                '18 - 24 anos':3,
                '11 - 14 anos':1,
                '15 - 17 anos':2, 
                '25 - 29 anos':4}

meses = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}

df = df[_colunas].copy()
df = df[_colunas].copy()
df.rename(columns=_coluna_rename, inplace = True)
df['Data'] = pd.to_datetime(df['Data'])
df['Mês-Numério'] = df['Data'].dt.month
df['Mês'] = df['Mês-Numério'].map(meses)
df['Ano'] = df['Data'].dt.year.astype(str)
df['Mês - Ano'] = df['Mês'] + '-' + df['Ano']
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)
df.sort_values(by=['Data'], inplace=True)
df.reset_index(drop=True, inplace=True)

# --- Adicionando filtros ---

# Filtro por intervalo de datas
data_inicial = st.sidebar.date_input("Data inicial", df['Data'].min())
data_final = st.sidebar.date_input("Data final", df['Data'].max())

# Filtro de idade
idade = st.sidebar.multiselect(
    "Faixa de idade:",
    options=df['Idade'].unique(),
    default=df['Idade'].unique()
)

# Filtro decisão

decisao = st.sidebar.multiselect(
    "Tipo de decisão:",
    options=df['Decisão'].unique(),
    default=df['Decisão'].unique()
)

# Filtro de batismo

batismo = st.sidebar.multiselect(
    "Situação referente ao batismo:",
    options=df['Batizado'].unique(),
    default=df['Batizado'].unique()
)

# Filtro de estado civil

estado_civil = st.sidebar.multiselect(
    "Estado civil:",
    options=df['Estado Civil'].unique(),
    default=df['Estado Civil'].unique()
)

# Filtro de convite

convite = st.sidebar.multiselect(
    "Como chegou na VIVA:",
    options=df['Forma de convite'].unique(),
    default=df['Forma de convite'].unique()
)

# Filtro de ambiente da decisão

ambiente = st.sidebar.multiselect(
    "Ambiente da decisão:",
    options=df['Período do culto'].unique(),
    default=df['Período do culto'].unique()
)

# Filtro de ano

# ano = st.sidebar.multiselect(
#     "Ano:",
#     options=df['Ano'].unique(),
#     default=df['Ano'].unique()
# )

# --- Aplicando filtros ---
df_filtrado = df[
    (df['Idade'].isin(idade)) &
    (df['Decisão'].isin(decisao)) &
    (df['Batizado'].isin(batismo)) &
    (df['Estado Civil'].isin(estado_civil)) &
    (df['Forma de convite'].isin(convite)) &
    (df['Período do culto'].isin(ambiente)) &
    # (df['Ano'].isin(ano)) &
    (df['Data'] >= pd.to_datetime(data_inicial)) &
    (df['Data'] <= pd.to_datetime(data_final))
].copy()

did = df_filtrado.groupby(['Idade', 'Decisão']).size().reset_index(name='N')
did['Idade ordenada'] = did['Idade'].map(_idade_ordem)

dib = df_filtrado.groupby(['Idade', 'Batizado']).size().reset_index(name='N')
dib['Idade ordenada'] = dib['Idade'].map(_idade_ordem)

dip = df_filtrado.groupby(['Idade', 'Período do culto']).size().reset_index(name='N')
dip['Idade ordenada'] = dip['Idade'].map(_idade_ordem)


# Gráficos

fig1 = px.bar(did, 
             x='Idade', 
             y='N', 
             color='Decisão', 
             barmode='group', 
             text='N',
             color_discrete_sequence=px.colors.qualitative.G10)

fig1.update_layout(template='plotly_dark',
                  yaxis_title='Quantidade de Decisões',
                  title='Decisões por Faixa Etária',
                  title_x=0.5)
fig1.update_traces(textposition='outside') 



fig2 = px.pie(df_filtrado, 
             names='Forma de convite',
             color_discrete_sequence=px.colors.qualitative.G10)

fig2.update_layout(template='plotly_dark',
                  title='Forma de convite',
                  title_x=0.5)

fig2.update_traces(textposition='outside') 

col11, col12 = st.columns([7, 3])

with col11:
    st.plotly_chart(fig1, use_container_width=True)

with col12:
    st.plotly_chart(fig2, use_container_width=True)


fig3 = px.bar(dib, 
             x='Idade', 
             y='N', 
             color='Batizado', 
             barmode='group', 
             text='N',
             color_discrete_sequence=px.colors.qualitative.G10)

fig3.update_layout(template='plotly_dark',
                  yaxis_title='Quantidade de Batizado e Não Batizados',
                  title='Batizados por Faixa Etária',
                  title_x=0.5)

fig3.update_traces(textposition='outside') 


fig4 = px.pie(df_filtrado, 
             names='Estado Civil',
             color_discrete_sequence=px.colors.qualitative.G10)

fig4.update_layout(template='plotly_dark',
                  title='Estado Civil',
                  title_x=0.5)

fig4.update_traces(textposition='outside') 

col21, col22 = st.columns([7, 3])

with col21:
    st.plotly_chart(fig3, use_container_width=True)

with col22:
    st.plotly_chart(fig4, use_container_width=True)

fig5 = px.bar(dip, 
             x='Idade', 
             y='N', 
             color='Período do culto', 
             barmode='group', 
             text='N',
             color_discrete_sequence=px.colors.qualitative.G10)

fig5.update_layout(template='plotly_dark',
                  yaxis_title='Quantidade de Batizado e Não Batizados',
                  title='Local da Decisão por Faixa Etária',
                  title_x=0.5)

fig5.update_traces(textposition='outside') 

# df_filtrado.sort_values(by='Mês-Numério', inplace=True)

fig6 = px.pie(df_filtrado, 
             names='Mês',
             color_discrete_sequence=px.colors.qualitative.G10)

fig6.update_layout(template='plotly_dark',
                  title='Mês',
                  title_x=0.5)
fig6.update_traces(textposition='outside')


col31, col32 = st.columns([7, 3])

with col31:
    st.plotly_chart(fig5, use_container_width=True)

with col32:
    st.plotly_chart(fig6, use_container_width=True)