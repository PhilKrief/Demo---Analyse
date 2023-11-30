import pandas as pd
import streamlit as st
import numpy as np
from utils import * 
from finance_functions import * 

def allocation_df_prep(allocation, df, returns):
    selected_row = df.loc[allocation]
    allocation_df = pd.DataFrame( columns= selected_row.index, index= returns.Période)
    allocation_df.loc[:,:] = selected_row.values
    return allocation_df


common_elements_investmentora()
page_header("Example des mandats GPD")

profiles = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
if st.session_state['mandat'] is not True:
    mandat = st.session_state["mandat"]
    st.session_state["profile"] = st.sidebar.multiselect("Quelle profile veux tu voir? ",options=profiles, default=mandat)
else:
    st.session_state["profile"] = st.sidebar.multiselect("Quelle profile veux tu voir? ",options=profiles, default="A")

st.session_state["periodes"] = st.sidebar.multiselect("Quelle periode veux tu voir? ",options=[1,3,5,10], default=1)

indice = st.sidebar.checkbox("Veux tu voir l'indices? ")
million = st.sidebar.checkbox("Veux tu voir l'évolution de $1,000,000 ")

fees = st.sidebar.number_input("Frais annuel")

rendements_df = pd.read_excel(st.session_state["datafile"] ,sheet_name="Rendements bruts")
indices_df = pd.read_excel(st.session_state["datafile"], sheet_name="Rendements indices")

allocation_profil = pd.read_excel(st.session_state["datafile"], sheet_name="Allocation").set_index(
'Code_Rendements').T

rendements_df["Year"] = pd.DatetimeIndex(rendements_df.Période).year
rendements_df["Month"] = pd.DatetimeIndex(rendements_df.Période).month


funds = ['Placement à court terme', 'Obligations gouvernementales', 'Obligations corporatives', 'Actions cdns grande cap', 'Actions cdns pet cap','Actions US Tax', 'Actions EAEO', 'Actions mondiales de PC', 'Actions des marchés émergents', 'Stratégies complémentaires', 'Stratégie à rendement absolu']

returns_df_calc = rendements_df[funds]
returns_df_calc['Encaisse'] = 0
returns_df_calc.index = rendements_df.Période

st.session_state['funddata'] =  returns_df_calc

indices_df_calc =  indices_df[funds]
indices_df_calc['Encaisse'] = 0
indices_df_calc.index = indices_df.Période

st.session_state['benchdata'] = indices_df_calc

rendement_mandat = pd.DataFrame(index=rendements_df.Période)
rendement_bench = pd.DataFrame(index=indices_df.Période)

for profile in profiles:
    allo = allocation_df_prep(profile, allocation_profil, rendements_df)
    rendement_mandat[profile] = (calculate_portfolio_returns(allo, returns_df_calc))
    allo_bench = allocation_df_prep(profile, allocation_profil, indices_df)
    rendement_bench[profile] = (calculate_portfolio_returns(allo, indices_df_calc))
    
graph_df = pd.DataFrame()
graph_df.index = rendement_mandat.index

if fees: 
    monthly = fees / 1200
    rendement_mandat = rendement_mandat - monthly

financial_metrics = pd.DataFrame()
financial_metrics['Index'] = ['Fonds', 'Date de début', 'Date de fin', 'Rendement brut (période)', 'Rendement indice (période)', 'Rendement brut (annualisée)', 'Rendement indice (annualisée)', 'Valeur ajoutée (période)', 'Valeur ajoutée annualisée', 'Risque actif annualisé', 'Ratio information', 'Beta', 'Alpha annualisé', 'Ratio sharpe', 'Coefficient de corrélation', 'Volatilité annualisée du fonds', "Volatilité annualisée de l'indice"]

if st.session_state["profile"] is not None:
    for profile in st.session_state['profile']:
        metrique = financial_metric_table(st.session_state["periodes"], rendement_mandat, rendement_bench, indices_df, profile)
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



rendement_mandat = ((1 + rendement_mandat).cumprod())
rendement_bench = ((1 + rendement_bench).cumprod())

if million:
    rendement_mandat_graph = rendement_mandat * 1000000
    rendement_bench_graph = rendement_bench * 1000000
else:
    rendement_mandat_graph = rendement_mandat 
    rendement_bench_graph = rendement_bench 


if st.session_state["profile"] is not None:
        for profile in st.session_state['profile']:
            #profile = st.session_state['profile']
            graph_df['profile %s'%profile] = rendement_mandat_graph[profile]
            if indice:
                graph_df['indice %s'%profile] = rendement_bench_graph[profile]

        
        st.line_chart(graph_df)
        return_col, risk_col = st.columns([1, 1])
        return_col.markdown("<h2 style='text-align: center;'>Rendement</h2>", unsafe_allow_html=True)
        return_col.dataframe(return_metrics, use_container_width=True)

        risk_col.markdown("<h2 style='text-align: center;'>Risque</h2>", unsafe_allow_html=True)
        risk_col.dataframe(risk_metrics, use_container_width=True)
        



