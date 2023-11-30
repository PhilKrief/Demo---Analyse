import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import copy 
from datetime import datetime, timedelta
import requests

def common_elements_investmentora():
    st.set_page_config(page_title="WM Tool", page_icon=":robot_face:", layout='wide')
    if "datafile" not in st.session_state:
        st.session_state["datafile"] = True
    if "network" not in st.session_state:
        st.session_state["network"] = True
    if "profile" not in st.session_state:
        st.session_state["profile"] = True
    if "funddata" not in st.session_state:
        st.session_state["funddata"] = True
    if "periodes" not in st.session_state:
        st.session_state["periodes"] = True
    if "personal_information" not in st.session_state:
        st.session_state["personal_information"] = True
    if 'risk_score' not in st.session_state:
        st.session_state['risk_score'] = True
    if 'mandat' not in st.session_state:    
        st.session_state['mandat'] = True
    if "portfolio" is not True:
        st.session_state["portfolio"] = True

    st.session_state["datafile"] = "Sources - PowerBI Dashboard - GPD_SSD_VMD RandomData.xlsx"

def page_header(page_title):
    st.markdown("<h1 style='text-align: center;'>Wealth Management Tool - Demo Version</h1>", unsafe_allow_html=True)
    header_text = f"<h2 style='text-align: center;'>{page_title} </h2>"
    st.markdown(header_text, unsafe_allow_html=True)
    st.write("---")  # Horizontal line for visual separation