import pandas as pd
import streamlit as st
import requests
import plotly.graph_objs as go
import yfinance as yf
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from deep_translator.exceptions import NotValidPayload, TooManyRequests
from pynvest.scrappers.fundamentus import Fundamentus

class Page:
    """Criar dashboard para monitoramento de ativos"""

    def __init__(self) -> None:
        pass

    def webpage(self) -> None:
        """Elaboração da page"""
        st.set_page_config(
            page_title="Monitor Financeiro",
            page_icon="💰",
            layout="wide",
        )

        st.markdown(
            """
        <div style="background-color:#880808";padding:10px;border-radius:20px">
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.sidebar.empty()
        st.sidebar.image("img/icon-monitor.png", width=150)
        st.sidebar.title("Stock Dash")
        st.sidebar.header("Insira os dados")

class Market:
    """Classe para obter os dados de forma de investimento e ativo"""

    def __init__(self, market_name: str) -> None:
        self.market = market_name

    def stock_list(self) -> list[str]:
        """Obtém lista de ativos para cada tipo"""
        tickers_scrapper = Fundamentus()
        if self.market == 'Ações':
            tickers = tickers_scrapper.extracao_tickers_de_ativos()
            return tickers
        else:
            tickers = tickers_scrapper.extracao_tickers_de_ativos(tipo="fiis")
            return tickers

    def stock_data(self, symbol: str, years: int) -> pd.DataFrame:
        """Gera dataframe com os dados dos ativos"""
        self.symbol_data = {}
        self.ticker = yf.Ticker(f'{symbol}.SA')
        self.stock = yf.Ticker(f'{symbol}.SA').history(period=f'{years}y')
        self.symbol_data[symbol] = pd.DataFrame(self.stock)
        df = self.symbol_data[symbol]
        return df

    def price_chart(self, symbol: str) -> None:
        """Gera gráfico com histórico de preço da cotação"""
        fig_cotacoes = go.Figure()

        for symbol, df in self.symbol_data.items():
            fig_cotacoes.add_trace(
                go.Scatter(x=pd.to_datetime(df.index),
                           y=df['Close'],
                           mode='lines',
                           name=symbol))

        fig_cotacoes.update_layout(legend=dict(orientation="h",
                                               yanchor="bottom",
                                               y=1.02,
                                               xanchor="right",
                                               x=1),
                                   yaxis_tickprefix='R$',
                                   yaxis_tickformat=',.2f',
                                   xaxis_title='Data',
                                   yaxis_title='Preço de Fechamento'
                                   )
        st.plotly_chart(fig_cotacoes)

    def website(self) -> str:
        """Coleta o website da empresa"""
        website = self.ticker.get_info()
        return str(website['website'])
    
    def description(self) -> str:
        """Coleta a descrição do ativo e traduz para português brasileiro"""
        try:
            info = self.ticker.get_info()
            description = info['longBusinessSummary']
            description_translated = GoogleTranslator(source='auto', target='pt').translate(description)
            return str(description_translated)
        except KeyError as e:
            translate_error = st.error(f"Erro: chave não encontrada no dicionário - {e}")
            return str(translate_error)
        except TooManyRequests as e:
            translate_error = st.error("Erro: Limite de requisições da API do GoogleTranslator excedido. Tente novamente mais tarde.")
            return str(translate_error)
        except NotValidPayload as e:
            translate_error = st.error(f"Erro: conteúdo inválido para tradução - {e}")
            return str(translate_error)
        except Exception as e:
            translate_error = st.error(f"Ocorreu um erro inesperado: {e}")
            return str(translate_error)

    def company_name(self) -> str:
        """Nome da empresa"""
        info = self.ticker.get_info()
        company_name = info['longName']
        return str(company_name)
        
    def dividends(self, symbol: str) -> None:
        """Coleta os dividendos distribúidos pela empresa"""
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',  # Do Not Track Request Header 
            'Connection': 'close'
        }

        stock_dv_urls = f'https://www.fundamentus.com.br/proventos.php?papel={symbol}&tipo=2'

        response = requests.get(stock_dv_urls, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        dividend_table = soup.find('table')
        dividends = pd.DataFrame(columns=[
            'Data', 'Valor', 'Tipo', 'Data de Pagamento', 'Por quantas ações'
        ])

        if dividend_table:
            for row in dividend_table.tbody.find_all('tr'):
                columns = row.find_all('td')
                if columns:
                    ult_data_table = columns[0].text.strip()
                    valor_table = columns[1].text.strip()
                    type_table = columns[2].text.strip()
                    data_pag_table = columns[3].text.strip()
                    qty_stock = columns[4].text.strip()
                    dividends = pd.concat([
                        dividends,
                        pd.DataFrame.from_records([{
                            'Data':
                            ult_data_table,
                            'Valor':
                            valor_table,
                            'Tipo':
                            type_table,
                            'Data de Pagamento':
                            data_pag_table,
                            'Por quantas ações':
                            qty_stock
                        }])
                    ])

            dividends['Valor'] = dividends['Valor'].str.replace(
                ',', '.').astype(float)
            dividends = dividends.drop(columns=['Por quantas ações'])
            dividends.set_index('Tipo', inplace=True)
            dividends = dividends.rename(columns={
                'Data': 'Registro',
                'Data de Pagamento': 'Pagamento'
            })

            dividends['Ano'] = pd.to_datetime(
                dividends['Registro'], dayfirst=True).dt.year.astype(str)
            dividends['Ano'] = dividends['Ano'].str.replace(',', '')

            self.dv = dividends

            # Obtendo o total de dividendos por ano
            self.total_dv_year = dividends.groupby(
                'Ano')['Valor'].sum().reset_index()

            self.total_dv_year = self.total_dv_year.tail(8)
        else:
            st.warning(f"Não foi possível obter dividendos de {symbol}")
            st.stop()

    def dividends_chart(self, symbol: str) -> None:
        """Gera gráfico de dividendos"""
        fig_dividends = go.Figure()
        fig_dividends.add_bar(x=self.total_dv_year['Ano'],
                              y=self.total_dv_year['Valor'],
                              marker_color='palegreen')

        fig_dividends.update_layout(
            xaxis_title='Ano',
            yaxis_title='Valor (R$)',
            yaxis_tickprefix='R$',
            yaxis_tickformat=',.2f',
        )

        for i, ano in enumerate(self.total_dv_year['Ano']):
            fig_dividends.add_annotation(
                x=ano,
                y=self.total_dv_year['Valor'].iloc[i],
                text=f"R$ {self.total_dv_year['Valor'].iloc[i]:,.2f}",
                showarrow=True,
                arrowhead=1,
                font=dict(size=13))
        st.plotly_chart(fig_dividends)

    def dividends_table(self) -> None:
        """Gera tabela de dividendos"""
        st.subheader("")
        st.dataframe(self.dv, width=850, height=350)

    def fii_dividends(self, symbol: str) -> None:
        """Coleta os dividendos distribúidos pelo fundo imobiliário"""
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',  # Do Not Track Request Header 
            'Connection': 'close'
        }

        stock_dv_urls = f'https://www.fundamentus.com.br/fii_proventos.php?papel={symbol}&tipo=2'

        response = requests.get(stock_dv_urls, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        dividend_table = soup.find('table')
        dividends = pd.DataFrame(columns=[
            'Última Data Com', 'Tipo', 'Data de Pagamento', 'Valor'
        ])

        if dividend_table:
            for row in dividend_table.tbody.find_all('tr'):
                columns = row.find_all('td')
                if columns:
                    ult_data_table = columns[0].text.strip()
                    type_table = columns[1].text.strip()
                    data_pag_table = columns[2].text.strip()
                    valor_table = columns[3].text.strip()
                    dividends = pd.concat([
                        dividends,
                        pd.DataFrame.from_records([{
                            'Última Data Com':
                            ult_data_table,
                            'Tipo':
                            type_table,
                            'Data de Pagamento':
                            data_pag_table,
                            'Valor':
                            valor_table,
                        }])
                    ])

            dividends['Valor'] = dividends['Valor'].str.replace(
                ',', '.').astype(float)
            dividends.set_index('Tipo', inplace=True)
            dividends = dividends.rename(columns={
                'Última Data Com': 'Registro',
                'Data de Pagamento': 'Pagamento'
            })

            dividends['Ano'] = pd.to_datetime(
                dividends['Registro'], dayfirst=True).dt.year.astype(str)
            dividends['Ano'] = dividends['Ano'].str.replace(',', '')

            self.dv = dividends

            # Obtendo o total de dividendos por ano
            self.total_dv_year = dividends.groupby(
                'Ano')['Valor'].sum().reset_index()

            self.total_dv_year = self.total_dv_year.tail(8)
        else:
            st.warning(f"Não foi possível obter dividendos de {symbol}")
            st.stop()

    def fii_dividends_chart(self, symbol: str) -> None:
        """Gera gráfico de dividendos"""
        fig_dividends = go.Figure()
        fig_dividends.add_bar(x=self.total_dv_year['Ano'],
                              y=self.total_dv_year['Valor'],
                              marker_color='palegreen')

        fig_dividends.update_layout(
            xaxis_title='Ano',
            yaxis_title='Valor (R$)',
            yaxis_tickprefix='R$',
            yaxis_tickformat=',.2f',
        )

        for i, ano in enumerate(self.total_dv_year['Ano']):
            fig_dividends.add_annotation(
                x=ano,
                y=self.total_dv_year['Valor'].iloc[i],
                text=f"R$ {self.total_dv_year['Valor'].iloc[i]:,.2f}",
                showarrow=True,
                arrowhead=1,
                font=dict(size=13))
        st.plotly_chart(fig_dividends)

    def fii_dividends_table(self) -> None:
        """Gera tabela de dividendos"""
        st.subheader("")
        st.dataframe(self.dv, width=850, height=350)