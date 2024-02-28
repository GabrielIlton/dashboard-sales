import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout = 'wide')

def formatAmount(amount, prefix = ''):
    for unit in ['', 'mil']:
        if amount < 1000:
            return f'{prefix} {amount:.2f} {unit}'
        amount /= 1000
    return f'{prefix} {amount:.2f} milhões'

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'
response = requests.get(url)

dados = pd.DataFrame.from_dict(response.json())

dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

income = dados['Preço'].sum()
sales = dados.shape[0]

## Tabelas
### Tabelas de Receitas
income_states = dados.groupby('Local da compra')[['Preço']].sum()
income_states = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(income_states, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

income_monthly = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].sum().reset_index()
income_monthly['Ano'] = income_monthly['Data da Compra'].dt.year
income_monthly['Mes'] = income_monthly['Data da Compra'].dt.month

income_categories = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending = False)

### Tabelas de Quantidade de Vendas
 ## DESAFIO
qtd_sale_states = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
qtd_sale_states = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(qtd_sale_states, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

### Tabelas Vendedores
sellers = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## Gráficos
income_states_fig_map = px.scatter_geo(income_states, lat = 'lat', lon = 'lon', scope = 'south america', size = 'Preço', template = 'seaborn', hover_name = 'Local da compra', hover_data = { 'lat': False, 'lon': False }, title = 'Receita por estado')

income_monthly_fig = px.line(income_monthly, x = 'Mes', y = 'Preço', markers = True, range_y = (0, income_monthly.max()), color = 'Ano', line_dash = 'Ano', title = 'Receita mensal')
income_monthly_fig.update_layout(yaxis_title = 'Receita')

income_states_fig = px.bar(income_states.head(), x = 'Local da compra', y = 'Preço', text_auto = True, title = 'Top estados (receita)')
income_states_fig.update_layout(yaxis_title = 'Receita')

income_categories_fig = px.bar(income_categories.head(), text_auto = True, title = 'Receita por categoria')
income_categories_fig.update_layout(yaxis_title = 'Receita')


qtd_sale_states_fig_map = px.scatter_geo(qtd_sale_states, lat = 'lat', lon = 'lon', scope = 'south america', size = 'Preço', template = 'seaborn', hover_name = 'Local da compra', hover_data = { 'lat': False, 'lon': False }, title = 'Vendas por estado')

## Visualização no streamlit
tab0, tab1, tab2, tab3 = st.tabs(['Tabela Geral', 'Receita', 'Quantidade de vendas', 'Vendedores'])

tab0.dataframe(dados)

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("RECEITA TOTAL", formatAmount(income), "R$")
        st.plotly_chart(income_states_fig_map, use_container_width = True)
        st.plotly_chart(income_states_fig, use_container_width = True)

    with col2:
        st.metric("QUANTIDADE DE VENDAS", formatAmount(sales))
        st.plotly_chart(income_monthly_fig, use_container_width = True)
        st.plotly_chart(income_categories_fig, use_container_width = True)

with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.metric("RECEITA TOTAL", formatAmount(income), "R$")
        st.plotly_chart(qtd_sale_states_fig_map, use_container_width = True)
    with col2:
        st.metric("QUANTIDADE DE VENDAS", formatAmount(sales))

with tab3:
    qtd_sellers = st.number_input('Quantidade de vendedores', 2, 10, 5)

    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("RECEITA TOTAL", formatAmount(income), "R$")
        
        income_sellers_fig = px.bar(sellers[['sum']].sort_values('sum', ascending = False).head(qtd_sellers), x = 'sum' , y = sellers[['sum']].sort_values('sum', ascending = False).head(qtd_sellers).index, text_auto = True, title = f'Top {qtd_sellers} vendedores (receita)')

        st.plotly_chart(income_sellers_fig, use_container_width = True)
    with col2:
        st.metric("QUANTIDADE DE VENDAS", formatAmount(sales))
        
        sale_sellers_fig = px.bar(sellers[['count']].sort_values('count', ascending = False).head(qtd_sellers), x = 'count' , y = sellers[['count']].sort_values('count', ascending = False).head(qtd_sellers).index, text_auto = True, title = f'Top {qtd_sellers} vendedores (quantidade de vendas)')

        st.plotly_chart(sale_sellers_fig, use_container_width = True)
