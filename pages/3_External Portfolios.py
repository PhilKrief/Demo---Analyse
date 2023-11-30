import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from utils import *
from finance_functions import *


key = "d8eabf9ca1dec61aceefd4b4a9b93992"
common_elements_investmentora()
page_header("Example des mandats GPD")


#start_date = st.sidebar.date_input("Date de Debut: ")
#end_date = st.sidebar.date_input("Date de fin: ")
#key = st.sidebar.text_input("API KEY: ")

uploaded_file = st.file_uploader("Upload your CSV or Excel file here", type=['csv', 'xlsx'])

if uploaded_file is not None:
    if uploaded_file.type == "text/csv":
        # Read CSV file
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        # Read Excel file
        df = pd.read_excel(uploaded_file)
else:
    df = pd.DataFrame(columns=['Ticker', 'Allocation'],index=np.arange(2))

edited_df = st.experimental_data_editor(df, num_rows="dynamic")
tickers = edited_df['Ticker'].tolist()

bench = st.selectbox(
    'Which benchmark will you choose ?',
    ('SPY', 'QQQ', 'DIA', "IWM"))

bench_prices = get_monthly_stock_portfolio_prices([bench], key)
bench_returns = calculate_returns(bench_prices)
bench_returns = bench_returns.rename({bench: "BenchmarkReturns"}, axis=1)

portfolio_prices = get_monthly_stock_portfolio_prices(tickers, key)
portfolio_returns = calculate_returns(portfolio_prices)

allocations = allocation_df(edited_df, portfolio_returns)
portfolio_returns = calculate_portfolio_returns(allocations, portfolio_returns)
portfolio_returns = portfolio_returns.rename("PortfolioReturns")
portfolio_returns = portfolio_returns.to_frame()


portfolio_returns = portfolio_returns[::-1]
bench_returns = bench_returns[::-1] 
######

st.session_state["periodes"] = st.sidebar.multiselect("Quelle periode veux tu voir? ",options=[1,3,5,10], default=1)

indice = st.sidebar.checkbox("Veux tu voir l'indices? ")
million = st.sidebar.checkbox("Veux tu voir l'évolution de $1,000,000 ")

fees = st.sidebar.number_input("Frais annuel (en decimale)")
risk_free_rate = st.sidebar.number_input("Taux sans risque (en decimale)", value=0.02)
indices_df = pd.DataFrame(index = bench_returns.index, columns=['Marché monétaire'])
indices_df['Marché monétaire'] = float(risk_free_rate)/12

    
graph_df = pd.DataFrame()
graph_df.index = portfolio_returns.index

if fees: 
    monthly = fees / 12
    portfolio_returns = portfolio_returns - monthly

financial_metrics = pd.DataFrame()
financial_metrics['Index'] = ['Fonds', 'Date de début', 'Date de fin', 'Rendement brut (période)', 'Rendement indice (période)', 'Rendement brut (annualisée)', 'Rendement indice (annualisée)', 'Valeur ajoutée (période)', 'Valeur ajoutée annualisée', 'Risque actif annualisé', 'Ratio information', 'Beta', 'Alpha annualisé', 'Ratio sharpe', 'Coefficient de corrélation', 'Volatilité annualisée du fonds', "Volatilité annualisée de l'indice"]

bench_returns = bench_returns.rename({"BenchmarkReturns": "PortfolioReturns"}, axis=1)
metrique = financial_metric_table(st.session_state["periodes"], portfolio_returns, bench_returns, indices_df, "PortfolioReturns")
cols = [i for i in list(metrique.columns) if i != 'Index']
financial_metrics[cols] = metrique[cols]

financial_metrics.set_index("Index", inplace=True)

percentage_rows = ["Rendement brut (période)", "Rendement indice (période)", "Rendement brut (annualisée)", "Rendement indice (annualisée)", "Valeur ajoutée (période)", "Valeur ajoutée annualisée","Volatilité annualisée du fonds", "Volatilité annualisée de l'indice"]
number_rows  = ["Risque actif annualisé", "Ratio information", "Beta", "Alpha annualisé", "Ratio sharpe", "Coefficient de corrélation"]

for row in percentage_rows:
    financial_metrics.loc[row,] = financial_metrics.loc[row,].astype(float)
    financial_metrics.loc[row,] = financial_metrics.loc[row,].apply('{:.2%}'.format)
for row in number_rows:
    financial_metrics.loc[row,] = financial_metrics.loc[row,].astype(float)
    financial_metrics.loc[row,] = financial_metrics.loc[row,].apply('{:.2}'.format)

return_rows = ["Rendement brut (période)", "Rendement indice (période)", "Rendement brut (annualisée)", "Rendement indice (annualisée)", "Valeur ajoutée (période)", "Valeur ajoutée annualisée"]

risk_rows = ["Risque actif annualisé", "Ratio information", "Beta", "Alpha annualisé", "Ratio sharpe", "Coefficient de corrélation", "Volatilité annualisée du fonds", "Volatilité annualisée de l'indice"]

return_metrics = financial_metrics.loc[return_rows,]
risk_metrics = financial_metrics.loc[risk_rows,]


rendement_mandat = ((1 + portfolio_returns).cumprod())
rendement_bench = ((1 + bench_returns).cumprod())
print(rendement_bench)
if million:
    rendement_mandat_graph = rendement_mandat * 1000000
    rendement_bench_graph = rendement_bench * 1000000
else:
    rendement_mandat_graph = rendement_mandat 
    rendement_bench_graph = rendement_bench 


#profile = st.session_state['profile']
graph_df['PortfolioReturns'] = rendement_mandat_graph['PortfolioReturns']
if indice:
    graph_df['BenchmarkReturns'] = rendement_bench_graph['PortfolioReturns']

        
st.line_chart(graph_df)
return_col, risk_col = st.columns([1, 1])
return_col.markdown("<h2 style='text-align: center;'>Rendement</h2>", unsafe_allow_html=True)
return_col.dataframe(return_metrics, use_container_width=True)

risk_col.markdown("<h2 style='text-align: center;'>Risque</h2>", unsafe_allow_html=True)
risk_col.dataframe(risk_metrics, use_container_width=True)


