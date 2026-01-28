import gspread
import streamlit as st
import os

@st.cache_resource
def conectar_planilha():
    if os.path.exists('credentials.json'):
        try:
            gc = gspread.service_account(filename='credentials.json')
        except Exception as e:
            st.error(f"Erro ao ler credentials.json: {e}")
            return None
    elif hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
        try:
            creds_dict = st.secrets["gcp_service_account"]
            gc = gspread.service_account_from_dict(creds_dict)
        except Exception as e:
            st.error(f"Erro nos Secrets: {e}")
            return None
    else:
        st.error("🚨 Erro Crítico: Nenhuma credencial encontrada.")
        return None
    return gc.open("DB_Education")