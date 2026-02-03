import streamlit as st
import pandas as pd
import database as db
from datetime import datetime, date
from modules.ui.core import kpi_card

# --- FUNÇÕES AUXILIARES ---
def converter_data(df, col_nome):
    """Converte coluna de data string (dd/mm/yyyy) para datetime object"""
    if col_nome in df.columns:
        df[col_nome] = pd.to_datetime(df[col_nome], format='%d/%m/%Y', errors='coerce')
    return df

def formatar_valor_dinamico(valor):
    """
    Formata o valor em R$ e ajusta o HTML para não quebrar o layout.
    """
    texto = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # AJUSTE DE LAYOUT:
    # 1. font-size: 22px (Menor que o padrão 28px dos outros cards para caber números grandes)
    # 2. white-space: nowrap (Impede que o número quebre em duas linhas)
    return f"<span style='font-size: 22px; white-space: nowrap;'>{texto}</span>"

def render_dashboard():
    try:
        # --- 1. FILTRO DE MÊS (TOPO) ---
        ano_atual = date.today().year
        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        
        opcoes_meses = [f"{meses[m]}/{ano_atual}" for m in range(1, 13)]
        mes_atual_idx = date.today().month - 1
        
        c_filtro, _ = st.columns([1, 3])
        with c_filtro:
            mes_selecionado_str = st.selectbox("", options=opcoes_meses, index=mes_atual_idx)
        
        # Extrai mês e ano
        nome_mes, ano_str = mes_selecionado_str.split('/')
        mes_num = list(meses.keys())[list(meses.values()).index(nome_mes)]
        ano_num = int(ano_str)

        # --- 2. CARREGAMENTO E TRATAMENTO DE DADOS ---
        
        # A) ALUNOS
        df_alunos_cad = db.get_alunos() 
        
        # B) FINANCEIRO
        df_financeiro = db.get_financeiro_geral()
        if not df_financeiro.empty:
            if df_financeiro['Valor'].dtype == 'object':
                df_financeiro['Valor'] = df_financeiro['Valor'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df_financeiro['Valor'] = pd.to_numeric(df_financeiro['Valor'], errors='coerce').fillna(0.0)
            df_financeiro = converter_data(df_financeiro, 'Data')

        # C) AULAS
        df_aulas = db.get_aulas()
        if not df_aulas.empty:
            df_aulas = converter_data(df_aulas, 'Data')

        # --- 3. CÁLCULO DOS KPIS ---

        # KPI 1: ALUNOS ATIVOS (Geral)
        qtd_alunos_ativos = 0
        if not df_alunos_cad.empty:
            if 'Status' in df_alunos_cad.columns:
                qtd_alunos_ativos = len(df_alunos_cad[df_alunos_cad['Status'] == 'Ativo'])
            else:
                qtd_alunos_ativos = len(df_alunos_cad)

        # --- FILTRAGEM TEMPORAL ---
        df_fin_mes = pd.DataFrame()
        if not df_financeiro.empty and 'Data' in df_financeiro.columns:
            df_fin_mes = df_financeiro[
                (df_financeiro['Data'].dt.month == mes_num) & 
                (df_financeiro['Data'].dt.year == ano_num)
            ]

        df_aulas_mes = pd.DataFrame()
        if not df_aulas.empty and 'Data' in df_aulas.columns:
            df_aulas_mes = df_aulas[
                (df_aulas['Data'].dt.month == mes_num) & 
                (df_aulas['Data'].dt.year == ano_num)
            ]

        # KPI 2: RECEITA TOTAL (Mês)
        receita_mes = 0.00
        qtd_vendas_mes = 0
        
        if not df_fin_mes.empty:
            entradas = df_fin_mes[
                (df_fin_mes['Tipo'] == 'Entrada') & 
                (df_fin_mes['Status'] == 'Pago')
            ]
            receita_mes = entradas['Valor'].sum()
            qtd_vendas_mes = len(entradas)

        # KPI 3: TOTAL DE AULAS (Mês)
        total_aulas_mes = len(df_aulas_mes)

        # --- 4. RENDERIZAÇÃO (Apenas Cards) ---
        
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            kpi_card("Alunos Ativos", str(qtd_alunos_ativos), "icon_alunos.png")
            
        with c2:
            # Valor formatado com fonte reduzida para alinhar com os outros
            valor_formatado = formatar_valor_dinamico(receita_mes)
            kpi_card("Receita Mensal", valor_formatado, "icon_money.png")
            
        with c3:
            kpi_card("Aulas no Mês", str(total_aulas_mes), "icon_aulas.png") 
            
        with c4:
            kpi_card("Vendas no Mês", str(qtd_vendas_mes), "icon_vendas.png")
        
        # FIM DA RENDERIZAÇÃO
        # (Gráficos e linhas divisórias foram removidos conforme solicitado)

    except Exception as e:
        st.error(f"Erro ao carregar dashboard: {e}")