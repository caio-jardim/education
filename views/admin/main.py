import streamlit as st
from modules.ui.core import header_page

# Importações dos novos arquivos locais
from .dashboard import render_dashboard
from .cadastros import render_cadastros

# Importações dos módulos de UI existentes (mantendo a lógica original)
from modules.ui import financeiro, vendas, aulas, professores, alunos

def show_admin(usuario, selected_page):
    
    # --- ROTEAMENTO PELO MENU LATERAL ---
    
    # 1. VISÃO GERAL (DASHBOARD)
    if selected_page == "Visão Geral":
        header_page("Visão Geral", "Indicadores de performance")
        render_dashboard()

    # 2. CADASTROS
    elif selected_page == "Cadastros":
        render_cadastros()
            
    # 3. VENDAS
    elif selected_page == "Vendas":
        header_page("Gestão de Vendas")
        vendas.form_renovacao_pacote()

    # 4. FINANCEIRO
    elif selected_page == "Financeiro":
        header_page("Financeiro")
        financeiro.show_financeiro()

    # 5. AULAS (HISTÓRICO)
    elif selected_page == "Aulas": 
        aulas.show_gestao_aulas()

    # 6. PROFESSORES (GESTÃO)
    elif selected_page == "Professores":
        professores.show_gestao_vinculos()
        
    # 7. ALUNOS (GESTÃO)
    elif selected_page == "Alunos":
        alunos.show_gestao_vinculos()