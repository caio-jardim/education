import streamlit as st
from modules.ui.core import header_page
from modules.ui import alunos, professores

def render_cadastros():
    # Subtítulo simples, sem linha divisória embaixo
    header_page("Cadastros")
    
    # CSS LOCAL: Remove o espaço padrão entre o final do texto acima e o começo das abas
    st.markdown("""
        <style>
            /* Remove margem inferior do header */
            div[data-testid="stVerticalBlock"] > div:has(h2) { margin-bottom: -20px !important; }
            /* Sobe as abas */
            .stTabs { margin-top: -10px !important; }
        </style>
    """, unsafe_allow_html=True)
    
    tab_aluno, tab_prof = st.tabs(["🎓 Novo Aluno", "👨‍🏫 Novo Professor"])
    
    with tab_aluno:
        alunos.form_novo_aluno()
        
    with tab_prof:
        professores.form_novo_professor()