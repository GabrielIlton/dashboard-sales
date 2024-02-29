import streamlit as st
import requests
import pandas as pd
import time

@st.cache_data
def convert_csv(dataframe):
    return dataframe.to_csv(index = False).encode('utf-8')

def success_message():
    success = st.success('Arquivo baixado com sucesso!', icon = "✅")
    time.sleep(5)
    success.empty()

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'   

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

with st.expander('Colunas'):
    columns = st.multiselect('Selacione as colunas', list(dados.columns), list(dados.columns))

st.sidebar.title('Filtros')

with st.sidebar.expander('Nome do produto'):
    products = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Categoria do produto'):
    categories = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())

with st.sidebar.expander('Preço do produto'):
    price = st.slider('Selecione o preço', 0, 5000, (0,5000))

with st.sidebar.expander('Frete da venda'):
    freight = st.slider('Frete', 0, 250, (0,250))

with st.sidebar.expander('Data da compra'):
    buy_date = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

with st.sidebar.expander('Vendedor'):
    sellers = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())

with st.sidebar.expander('Local da compra'):
    buy_local = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())

with st.sidebar.expander('Avaliação da compra'):
    evaluation = st.slider('Selecione a avaliação da compra', 1, 5, value = (1,5))

with st.sidebar.expander('Tipo de pagamento'):
    payment_type = st.multiselect('Selecione o tipo de pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

with st.sidebar.expander('Quantidade de parcelas'):
    qtd_installments = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))

query = '''
Produto in @products and \
`Categoria do Produto` in @categories and \
@price[0] <= Preço <= @price[1] and \
@freight[0] <= Frete <= @freight[1] and \
@buy_date[0] <= `Data da Compra` <= @buy_date[1] and \
Vendedor in @sellers and \
`Local da compra` in @buy_local and \
@evaluation[0] <= `Avaliação da compra` <= @evaluation[1] and \
`Tipo de pagamento` in @payment_type and \
@qtd_installments[0] <= `Quantidade de parcelas` <= @qtd_installments[1]
'''

dados_filtrered = dados.query(query)
dados_filtrered = dados_filtrered[columns]

st.dataframe(dados_filtrered)

st.markdown(f'A tabela possui :blue[{dados_filtrered.shape[0]}] linhas e :blue[{dados_filtrered.shape[1]} colunas]')

st.markdown('Escreva um nome para o arquivo')

col1, col2 = st.columns(2)

with col1:
    filename = st.text_input('', label_visibility='collapsed', value='dados')
    filename += '.csv'

with col2:
    st.download_button('Baixar arquivo em csv', data = convert_csv(dados_filtrered), file_name = filename, mime = 'text/csv', on_click = success_message)
