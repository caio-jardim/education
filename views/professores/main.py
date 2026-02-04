import streamlit as st
from modules.ui.core import header_page

# Importações das views
from .agenda import show_agenda
from .alunos import show_page_alunos
from .aulas import show_page_aulas

def show_professor(usuario, selected_page):
    
    # --- 1. RECUPERAÇÃO INTELIGENTE DO ID ---
    # Tenta vários nomes possíveis para a coluna de ID no CAD_Usuarios
    id_prof = (
        usuario.get('ID Professor') or 
        usuario.get('ID Link') or 
        usuario.get('ID Vinculo') or 
        usuario.get('id_professor') or
        usuario.get('ID')
    )
    
    nome_prof = usuario.get('Nome Usuário') or usuario.get('Nome') or "Professor"

    # --- 2. DEBUG DE LOGIN (Para descobrirmos o nome certo da coluna) ---
    if not id_prof:
        st.error("⚠️ ERRO CRÍTICO: ID do Professor não identificado no login.")
        with st.expander("🕵️ Ver dados do Usuário (Debug)"):
            st.write("O sistema carregou estes dados do seu login:")
            st.json(usuario) # Mostra o dicionário inteiro para você ver a chave certa
            st.warning("Verifique se na aba 'CAD_Usuarios' existe uma coluna com o ID do professor preenchido.")
        return # Para aqui se não tiver ID
    # -------------------------------------------------------------------

    # --- 3. ROTEAMENTO ---
    
    # A. MEUS ALUNOS
    if selected_page == "Meus Alunos":
        show_page_alunos(id_prof, nome_prof)

    # B. MINHAS AULAS
    elif selected_page == "Minhas Aulas": 
        show_page_aulas(id_prof, nome_prof)

    # C. AGENDA (NOVO)
    elif selected_page == "Agenda":
        show_agenda(id_prof, nome_prof)