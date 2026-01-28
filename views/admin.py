import streamlit as st
import pandas as pd
import database as db
from datetime import date # <--- NOVO IMPORT NECESSÁRIO

# --- IMPORTAÇÃO DOS MÓDULOS DE UI ---
from modules.ui import alunos, financeiro, professores, vendas 
from modules.ui.core import kpi_card, header_page

def show_admin(usuario, selected_page):
    
    # --- ROTEAMENTO PELO MENU LATERAL ---
    
    # 1. VISÃO GERAL (DASHBOARD)
    if selected_page == "Visão Geral":
        header_page("Visão Geral", "Indicadores de performance")
        
        try:
            # --- CARREGAMENTO DE DADOS ---
            df_alunos = db.get_saldo_alunos()
            df_financeiro = db.get_financeiro_geral() 
            df_aulas = db.get_aulas() # <--- Carregamos as aulas aqui agora
            
            # --- CÁLCULO 1: ALUNOS ATIVOS ---
            qtd_alunos_ativos = 0
            if not df_alunos.empty:
                # Verifica se a coluna Status existe (segurança)
                if 'Status' in df_alunos.columns:
                    # Filtra apenas onde Status é exatamente 'Ativo'
                    filtro_ativos = df_alunos[df_alunos['Status'] == 'Ativo']
                    qtd_alunos_ativos = len(filtro_ativos)
                else:
                    # Se não tiver coluna status, conta tudo (fallback)
                    qtd_alunos_ativos = len(df_alunos)
            
            # --- CÁLCULO 2: AULAS HOJE ---
            qtd_aulas_hoje = 0
            if not df_aulas.empty:
                # Pega data de hoje e transforma em texto "dd/mm/yyyy" para bater com o Excel
                hoje_str = date.today().strftime("%d/%m/%Y")
                
                # Verifica se a coluna Data existe
                if 'Data' in df_aulas.columns:
                    # Filtra as aulas onde a Data é igual a hoje
                    filtro_hoje = df_aulas[df_aulas['Data'] == hoje_str]
                    qtd_aulas_hoje = len(filtro_hoje)

            # --- CÁLCULO 3: RECEITA ---
            receita_total = 0.00
            if not df_financeiro.empty:
                # Tratamento de string para float (R$)
                if df_financeiro['Valor'].dtype == 'object':
                    df_financeiro['Valor'] = df_financeiro['Valor'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
                
                entradas = df_financeiro[
                    (df_financeiro['Tipo'] == 'Entrada') & 
                    (df_financeiro['Status'] == 'Pago')
                ]
                receita_total = entradas['Valor'].sum() if not entradas.empty else 0.00

            # --- RENDERIZAÇÃO DOS CARDS ---
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                # Agora usa a variável filtrada qtd_alunos_ativos
                kpi_card("Alunos Ativos", str(qtd_alunos_ativos), "icon_alunos.png")
            with c2:
                kpi_card("Receita Total", f"R$ {receita_total:,.2f}", "icon_money.png")
            with c3:
                # Agora usa a variável filtrada qtd_aulas_hoje
                kpi_card("Aulas Hoje", str(qtd_aulas_hoje), "icon_aulas.png") 
            with c4:
                kpi_card("Novas Vendas", "3", "icon_vendas.png") # Placeholder (pode ajustar depois)
            
            st.divider()
            
            # --- GRÁFICOS ---
            st.markdown("### 📈 Performance Recente")
            if not df_financeiro.empty:
                st.bar_chart(df_financeiro, x="Data", y="Valor", color="Tipo")
            else:
                st.info("Sem dados financeiros para gerar gráficos.")

        except Exception as e:
            st.error(f"Erro ao carregar dashboard: {e}")

    # 2. CADASTROS
    elif selected_page == "Cadastros":
        header_page("Cadastros", "Gerencie alunos e professores")
        
        tab1, tab2 = st.tabs(["🎓 Novo Aluno", "👨‍🏫 Novo Professor"])
        
        with tab1:
            alunos.form_novo_aluno()
            
        with tab2:
            professores.form_novo_professor()

    # 3. VENDAS
    elif selected_page == "Vendas":
        header_page("Gestão de Vendas", "Renovação e venda de pacotes")
        vendas.form_renovacao_pacote()

    # 4. FINANCEIRO
    elif selected_page == "Financeiro":
        header_page("Financeiro", "Fluxo de caixa detalhado")
        financeiro.show_financeiro()

    # 5. AULAS (HISTÓRICO)
    elif selected_page == "Aulas": 
        header_page("Histórico de Aulas", "Registro geral da escola")
        df_aulas = db.get_aulas()
        
        if not df_aulas.empty:
            st.dataframe(
                df_aulas, 
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhuma aula registrada até o momento.")