import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import pandas as pd

# Configuração da página
st.set_page_config(page_title='Dashboard Financeiro Futurístico', layout='wide')

# Função para obter dados de ações
def get_stock_data(ticker, period='1d', interval='1m'):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        return data
    except Exception as e:
        st.error(f'Erro ao buscar dados do ativo {ticker}: {str(e)}')
        return None

# Função para obter os ativos que mais valorizaram na semana
def get_top_performers(tickers):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        top_performers = []
        
        for ticker in tickers:
            data = yf.download(ticker, start=start_date, end=end_date)
            if not data.empty:
                start_price = data.iloc[0]['Close']
                end_price = data.iloc[-1]['Close']
                change = ((end_price - start_price) / start_price) * 100
                top_performers.append((ticker, change))
        
        top_performers.sort(key=lambda x: x[1], reverse=True)
        return top_performers
    except Exception as e:
        st.error(f'Erro ao buscar ativos que mais valorizaram na semana: {str(e)}')
        return []

# Função para obter notícias financeiras
def get_financial_news(api_key, query='finance'):
    try:
        url = f'https://newsapi.org/v2/everything?q={query}&apiKey={api_key}'
        response = requests.get(url)
        data = response.json()
        
        if 'articles' in data:
            return data['articles']
        else:
            st.error(f'Erro ao buscar notícias financeiras: {str(data)}')
            return []
    except Exception as e:
        st.error(f'Erro ao buscar notícias financeiras: {str(e)}')
        return []

# Configurações da API News API
news_api_key = '9eb39a7fe7c94564995d4988bca51040'  # Substitua pela sua chave da API News

# Lista de ativos
ativos_disponiveis = ['AAPL', 'GOOG', 'MSFT', 'TSLA', 'AMZN', 'NFLX', 'META']

# Título
st.title('Mercado Financeiro')

# Layout da Barra Lateral
st.sidebar.header('Configurações do Ativo')
ativo = st.sidebar.text_input('Digite o símbolo do ativo:', 'AAPL').upper()
periodo = st.sidebar.selectbox('Selecione o período:', ['1d', '5d', '1mo', '3mo', '6mo', '1y'])
intervalo = st.sidebar.selectbox('Selecione o intervalo:', ['1m', '5m', '15m', '30m', '1h', '1d'])
grafico_tipo = st.sidebar.selectbox('Selecione o tipo de gráfico:', ['Candlestick', 'Linha', 'Área', 'Volume'])

# Carregar dados do ativo
dados = get_stock_data(ativo, periodo, intervalo)

# Adiciona o estilo CSS para o layout e animações
st.markdown("""
<style>
    @keyframes gradientBackground {
        0% { background-position: 0% 0%; }
        50% { background-position: 100% 100%; }
        100% { background-position: 0% 0%; }
    }

    body {
        background: linear-gradient(45deg, #2d2d2d, #1e1e1e);
        background-size: 400% 400%;
        animation: gradientBackground 15s ease infinite;
        color: #e1e1e1;
        font-family: Arial, sans-serif;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
        transition: background-color 0.3s, transform 0.3s;
    }

    .stButton>button:hover {
        background-color: #3e9fd0;
        animation: pulse 1s infinite;
    }

    .stPlotlyChart {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        margin: 20px 0;
        padding: 10px;
        width: 100%;
        max-width: 1200px;
        height: 500px;
    }

    .news-card {
        background-color: #333;
        border: 1px solid #444;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        transition: transform 0.3s, box-shadow 0.3s;
    }

    .news-card:hover {
        transform: scale(1.03);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    .news-card img {
        border-radius: 8px;
        width: 100%;
        height: auto;
    }

    .news-card a {
        text-decoration: none;
        color: inherit;
    }

    .news-card a:hover {
        color: #1f77b4;
    }

    .news-card .news-title {
        color: #1f77b4;
        font-weight: bold;
        font-size: 1.1em;
    }

    .news-card p {
        margin: 5px 0;
    }

    .news-separator {
        border-top: 1px solid #444;
        margin: 10px 0;
    }

    .table-container {
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

if dados is not None:
    # Gráfico baseado no tipo selecionado
    if grafico_tipo == 'Candlestick':
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.02, subplot_titles=(ativo, 'Volume'), 
                            row_width=[0.2, 0.7])

        fig.add_trace(go.Candlestick(x=dados.index,
                                     open=dados['Open'],
                                     high=dados['High'],
                                     low=dados['Low'],
                                     close=dados['Close'], name='Candlesticks',
                                     increasing_line_color='green', decreasing_line_color='red',
                                     showlegend=False), 
                      row=1, col=1)
        
        fig.add_trace(go.Bar(x=dados.index, y=dados['Volume'], name='Volume', marker_color='lightblue'), row=2, col=1)

        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showline=False, tickformat='%Y-%m-%d'),
            yaxis=dict(showgrid=True, zeroline=False, showline=False, title='Preço'),
            yaxis2=dict(showgrid=True, zeroline=False, showline=False, title='Volume'),
            paper_bgcolor='#1e1e1e',
            plot_bgcolor='#2d2d2d',
            font=dict(color='#e1e1e1'),
            title=f'{ativo} Preço e Volume',
            title_x=0.5,
            template='plotly_dark'
        )

    elif grafico_tipo == 'Linha':
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dados.index, y=dados['Close'], mode='lines', name='Fechamento', line=dict(color='cyan')))

        fig.update_layout(
            title=f'{ativo} Preço de Fechamento',
            xaxis_title='Data',
            yaxis_title='Preço',
            paper_bgcolor='#1e1e1e',
            plot_bgcolor='#2d2d2d',
            font=dict(color='#e1e1e1'),
            template='plotly_dark'
        )

    elif grafico_tipo == 'Área':
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dados.index, y=dados['Close'], mode='lines', fill='tozeroy', name='Fechamento', line=dict(color='cyan')))

        fig.update_layout(
            title=f'{ativo} Preço de Fechamento - Área',
            xaxis_title='Data',
            yaxis_title='Preço',
            paper_bgcolor='#1e1e1e',
            plot_bgcolor='#2d2d2d',
            font=dict(color='#e1e1e1'),
            template='plotly_dark'
        )

    elif grafico_tipo == 'Volume':
        fig = go.Figure()
        fig.add_trace(go.Bar(x=dados.index, y=dados['Volume'], name='Volume de Transações', marker_color='lightblue'))

        fig.update_layout(
            title=f'{ativo} Volume de Transações',
            xaxis_title='Data',
            yaxis_title='Volume',
            paper_bgcolor='#1e1e1e',
            plot_bgcolor='#2d2d2d',
            font=dict(color='#e1e1e1'),
            template='plotly_dark'
        )

    # Exibe o gráfico
    st.plotly_chart(fig, use_container_width=True)

# Seção de ativos que mais valorizaram na semana
st.sidebar.header('Top Performers da Semana')
tickers = ['AAPL', 'GOOG', 'MSFT', 'TSLA', 'AMZN', 'NFLX', 'META']  # Adicione mais tickers conforme necessário
top_performers = get_top_performers(tickers)

if top_performers:
    st.sidebar.subheader('Ativos que Mais Valorizaram na Semana')
    st.sidebar.write(pd.DataFrame(top_performers, columns=['Ticker', 'Variação (%)']).to_html(escape=False), unsafe_allow_html=True)
else:
    st.sidebar.write('Nenhum dado disponível.')

# Seção de notícias financeiras
st.header('')

news_articles = get_financial_news(news_api_key)

if news_articles:
    news_by_date = {}
    for article in news_articles:
        date = article.get('publishedAt', '').split('T')[0]
        if date not in news_by_date:
            news_by_date[date] = []
        news_by_date[date].append(article)

    st.subheader('Notícias Financeiras')
    for date, articles in sorted(news_by_date.items(), reverse=True):
        st.subheader(date)
        cols = st.columns(min(len(articles), 3))
        for i, article in enumerate(articles):
            title = article.get('title', 'Sem título')
            description = article.get('description', 'Sem descrição')
            url = article.get('url', '#')
            url_to_image = article.get('urlToImage', '')
            published_at = article.get('publishedAt', 'Desconhecido')
            
            with cols[i % 3]:
                st.markdown(f"""
                <div class="news-card">
                    <a href="{url}" target="_blank">
                        <p class="news-title">{title}</p>
                    </a>
                    <p>{description}</p>
                    {f'<img src="{url_to_image}" />' if url_to_image else ''}
                    <p style="font-size: 0.8em; color: #888;">Publicado em: {published_at}</p>
                    <div class="news-separator"></div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.write('Não há notícias disponíveis no momento.')
