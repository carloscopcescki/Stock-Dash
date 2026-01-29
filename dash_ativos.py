from functions import *
from fundamentals import FII_Data, Fundamental
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards

stock_dashboard = Page()
stock_dashboard.webpage()

# Definindo tipos e índices
markets = ['Ações', 'Fundos Imobiliários']

# Tipos e ativos
get_market = str(
    st.sidebar.selectbox("Escolha um tipo de renda variável", [''] + markets))
if get_market == "Ações":
    try:
        market = Market(get_market)
        stock_list = market.stock_list()
        stock = str(st.sidebar.selectbox("Escolha um ativo",
                                         [''] + stock_list))
        periodo = int(st.sidebar.number_input("Insira o período (em anos)", step=1, value=1, min_value=1, max_value=10))
        if stock:
            fundamental_data = Fundamental(stock)
            ticker = fundamental_data.ticker()
            market.stock_data(stock, periodo)
            
            col_img, col_name = st.columns(2)

            with col_img:
                if fundamental_data.ticker() == "ISAE4" or fundamental_data.ticker() == "ISAE3":
                    img = st.image(f"https://raw.githubusercontent.com/thecartera/B3-Assets-Images/refs/heads/main/imgs/TRPL4.png",
                                  width=120)
                elif fundamental_data.ticker() == "CXSE3":
                    img = st.image("https://www.ivalor.com.br/media/emp/logos/CXSE.png", width=120)
                elif fundamental_data.ticker() == "AXIA3" or fundamental_data.ticker() == "AXIA6":
                    img = st.image("https://www.ivalor.com.br/media/emp/logos/AXIA.png", width=120)
                else:
                    img = st.image(
                        f"https://raw.githubusercontent.com/thecartera/B3-Assets-Images/refs/heads/main/imgs/{stock}.png",
                        width=120)
            with col_name:
                st.header(market.company_name())

            st.markdown(f"**Código de negociação:** {fundamental_data.ticker()}")
            st.markdown(f"**Setor:** {fundamental_data.sector()}")
            st.markdown(f"**Segmento:** {fundamental_data.sub_sector()}")
            st.markdown(f"**Site:**  {market.website()}") 
            
            st.sidebar.divider()
            st.sidebar.link_button(f"Dados de {stock}", url=f"https://investidor10.com.br/acoes/{stock}/")
            st.sidebar.link_button(f"Notícias sobre {stock}", url=f"https://investidor10.com.br/noticias/ativo/{stock}/")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                col1.metric(label="Valor da cotação", value=f"R$ {fundamental_data.price()}", delta=f"{fundamental_data.variation()}")
            with col2:
                col2.metric(label="Dividend Yield", value=fundamental_data.dividend_yield())
            with col3:
                col3.metric(label="PL", value=fundamental_data.pl())
            with col4:
                col4.metric(label="PVP", value=fundamental_data.pvp())

            style_metric_cards(border_left_color='#292D34',
                               border_color='#292D34', background_color='#0e1111')

            st.header(f"Cotação {stock}", divider="grey")
            market.price_chart(stock)

            st.header(f"Dividendos {stock}", divider="grey")
            market.dividends(stock)

            colDividendChart, colDividendTable = st.columns(2)
            with colDividendChart:
                market.dividends_chart(stock)
            with colDividendTable:
                market.dividends_table()

            st.header(f"Indicadores Fundamentalistas {stock}", divider="grey")

            col1a, col1b, col1c, col1d, col1e, col1f = st.columns(6)
            with col1a:
                st.metric(label="P/L", value=fundamental_data.pl())
                st.metric(label="Margem Bruta", value=fundamental_data.marg_bruta())
                st.metric(label="ROIC", value=fundamental_data.roic())
            with col1b:
                st.metric(label="P/VP", value=fundamental_data.pvp())
                st.metric(label="Margem Ebit", value=fundamental_data.marg_ebit())
                st.metric(label="ROE", value=fundamental_data.roe())
            with col1c:
                st.metric(label="P/Receita (PSR)", value=fundamental_data.psr())
                st.metric(label="Margem Líquida", value=fundamental_data.marg_liquida())
            with col1d:
                st.metric(label="Dividend Yield", value=fundamental_data.dividend_yield())
                st.metric(label="Dívida Bruta Patrimônial", value=fundamental_data.div_bruta_patrim())
            with col1e:
                st.metric(label="EV/EBIT", value=fundamental_data.ev_ebit())
                st.metric(label="VPA", value=fundamental_data.vpa())
            with col1f:
                st.metric(label="EV/EBITDA", value=fundamental_data.ev_ebitda())
                st.metric(label="LPA", value=fundamental_data.lpa())

            st.header(f"Informações sobre {fundamental_data.ticker()}", divider="grey")

            colInfo1, colInfo2, colInfo3, colInfo4 = st.columns(4)
            with colInfo1:
                st.write(f"**Valor de mercado**")
                st.write(f"R$ {fundamental_data.market_value()}")
                st.write(f"**N° de cotas**")
                st.write(fundamental_data.ticker_quantity())
                st.write(f"**Dívida Bruta**")
                st.write(f"R$ {fundamental_data.debt_brut()}")
            with colInfo2:
                st.write(f"**Valor de firma**")
                st.write(f"R$ {fundamental_data.enterprise_value()}")
                st.write(f"**Ativos**")
                st.write(f"R$ {fundamental_data.ativos()}")
                st.write(f"**Dívida Líquida**")
                st.write(f"R$ {fundamental_data.debt_liq()}")
            with colInfo3:
                st.write(f"**Patrimônio Líquido**")
                st.write(f"R$ {fundamental_data.ticker_patrim()}")
                st.write(f"**Ativo Circulante**")
                st.write(f"R$ {fundamental_data.ativos_circulantes()}")
                st.write(f"**Disponibilidades**")
                st.write(f"R$ {fundamental_data.ticker_disp()}")
            with colInfo4:
                st.write(f"**Receita Líquida**")
                st.write(f"R$ {fundamental_data.net_revenue()}")
                st.write(f"**EBIT**")
                st.write(f"R$ {fundamental_data.ebit()}")
                st.write(f"**Lucro Líquido**")
                st.write(f"R$ {fundamental_data.net_profit()}")
                
            st.header(f"Sobre {fundamental_data.ticker()}", divider="grey")
            st.write(market.description())
        else:
            st.warning("Selecione um ativo")
    except Exception as e:
        st.error(f"Erro ao buscar os dados: {e}")

if get_market == "Fundos Imobiliários":
    try:
        market = Market(get_market)
        stock_list = market.stock_list()
        stock = str(st.sidebar.selectbox("Escolha um ativo",
                                         [''] + stock_list))
        periodo = int(st.sidebar.number_input("Insira o período (em anos)", step=1, value=1, min_value=1, max_value=10))
        
        if stock:
            st.sidebar.divider()
            st.sidebar.link_button(f"Dados de {stock}", url=f"https://investidor10.com.br/fiis/{stock}/")
            st.sidebar.link_button(f"Notícias sobre {stock}", url=f"https://investidor10.com.br/noticias/ativo/{stock}/")
            
            fii_data = FII_Data(stock)
            ticker = fii_data.fii_ticker()
            market.stock_data(stock, periodo)
            
            col_img, col_name = st.columns(2)
            with col_img:
                img = st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQRz2D2twD0bV62AwgI4vG6NXPrgt-rmw86XA&s", width=120)
            with col_name:
                st.header(fii_data.fii_name())

            col_fii_info1, col_fii_info2 = st.columns(2)
            with col_fii_info1:
                st.markdown(f"**Código de negociação:** {fii_data.fii_ticker()}")
                st.markdown(f"**Setor:** {fii_data.fii_type()}")
                st.markdown(f"**Segmento:** {fii_data.fii_segment()}")
                st.markdown(f"**Gestão:** {fii_data.fii_management()}")

            with col_fii_info2:
                st.markdown(f"**Comunicados:** https://www.fundamentus.com.br/fii_fatos_relevantes.php?papel={stock}")
                st.markdown(f"**Relatórios:** https://www.fundamentus.com.br/fii_relatorios.php?papel={stock}")
                st.markdown(f"**Imóveis:** https://www.fundamentus.com.br/fii_imoveis_detalhes.php?papel={stock}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(label="Valor da cotação", value=f"R$ {fii_data.fii_value()}", delta=f"{fii_data.fii_variation()}")
            col2.metric(label="Dividend Yield", value=fii_data.fii_dy())
            col3.metric(label="P/VP", value=fii_data.fii_pvp())
            col4.metric(label="Valor de Mercado", value=f'R$ {fii_data.fii_market_value()}')

            style_metric_cards(border_left_color='#292D34',
                               border_color='#292D34', background_color='#0e1111')
            
            st.header(f"Cotação de {stock}", divider="grey")
            market.price_chart(stock)

            st.header(f"Dividendos de {stock}", divider="grey")
            market.fii_dividends(stock)

            colDividendChart, colDividendTable = st.columns(2)
            with colDividendChart:
                market.fii_dividends_chart(stock)
            with colDividendTable:
                market.fii_dividends_table()

            st.header(f"Dados de {stock}", divider="grey")
            col1a, col1b, col1c, col1d = st.columns(4)
            with col1a:
                st.markdown(f"**FFO Yield:** {fii_data.fii_ffoyield()}")
                st.markdown(f"**Dividend Yield:** {fii_data.fii_dy()}")
                st.markdown(f"**FFO:** R$ {fii_data.fii_ffo()}")
            with col1b:
                st.markdown(f"**FFO/Cota:** {fii_data.fii_ffoticker()}")
                st.markdown(f"**Dividendo/Cota:** {fii_data.fii_divticker()}")
                st.markdown(f"**Rendimento Distribuído:** R$ {fii_data.fii_distributed_income()}")
            with col1c:
                st.markdown(f"**P/VP:** {fii_data.fii_pvp()}")
                st.markdown(f"**VP/Cota:** {fii_data.fii_vpticker()}")
                st.markdown(f"**Ativos:** R$ {fii_data.fii_assets()}")
            with col1d:
                st.markdown(f"**Receita:** R$ {fii_data.fii_revenue()}")
                st.markdown(f"**Venda de ativos:** R$ {fii_data.fii_sale()}")
                st.markdown(f"**Patrimônio Líquido:** R$ {fii_data.fii_patrim()}")
            
        else:
            st.warning("Selecione um tipo de renda variável")
    except Exception as e:
        st.error(f"Erro ao buscar os dados: {e}")
