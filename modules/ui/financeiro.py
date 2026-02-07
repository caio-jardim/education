import streamlit as st
import database as db
from datetime import date, datetime
import pandas as pd

def show_financeiro():
    st.markdown("### 💸 Fluxo de Caixa")
    
    # --- FORMULÁRIO DE LANÇAMENTO (MANTIDO IGUAL) ---
    with st.expander("➕ Novo Lançamento", expanded=False):
        with st.form("form_financeiro_geral", clear_on_submit=True, enter_to_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                tipo = st.radio("Tipo", ["Saída (Despesa)", "Entrada (Receita)"], horizontal=True)
                if "Saída" in tipo: cats = ["Pagamento Professores", "Salários", "Aluguel", "Software", "Marketing", "Outros"]
                else: cats = ["Venda Pacote", "Aporte", "Outros"]
                categoria = st.selectbox("Categoria", cats)
                descricao = st.text_input("Descrição", placeholder="Ex: Conta de Luz")

            with c2:
                valor = st.number_input("Valor (R$)", min_value=0.01, step=10.00, format="%.2f")
                data_mov = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
                pago = st.checkbox("Pago/Recebido?", value=True)
                status = "Pago" if pago else "Pendente"

            if st.form_submit_button("💾 Registrar"):
                if not descricao: st.error("Descrição obrigatória.")
                else:
                    try:
                        data_str = data_mov.strftime("%d/%m/%Y")
                        tipo_final = "Saída" if "Saída" in tipo else "Entrada"
                        db.registrar_movimentacao_financeira(data_str, tipo_final, categoria, descricao, valor, status)
                        st.success(f"Salvo: R$ {valor:.2f}")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e: st.error(f"Erro: {e}")

    st.divider()
    
    # --- CARREGAMENTO E FILTRO (NOVO!) ---
    df_fin = db.get_financeiro_geral()
    
    if not df_fin.empty:
        # 1. Tratamento numérico (Sua lógica original)
        df_fin['Valor_Num'] = pd.to_numeric(df_fin['Valor'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)
        
        # 2. Tratamento de Data (Necessário para o filtro)
        # Converte a coluna string 'Data' para datetime object
        df_fin['Data_Dt'] = pd.to_datetime(df_fin['Data'], format="%d/%m/%Y", errors='coerce')
        
        # Cria coluna auxiliar de "Mês/Ano" (ex: 02/2026)
        df_fin['Mes_Ano'] = df_fin['Data_Dt'].dt.strftime("%m/%Y")
        
        # 3. Criação do Seletor de Mês
        # Pega meses únicos e ordena do mais recente para o mais antigo
        lista_meses = sorted(df_fin['Mes_Ano'].dropna().unique(), key=lambda x: datetime.strptime(x, "%m/%Y"), reverse=True)
        lista_opcoes = ["Todos"] + list(lista_meses)
        
        col_filtro, col_vazio = st.columns([1, 3])
        with col_filtro:
            mes_selecionado = st.selectbox("📅 Filtrar Mês", options=lista_opcoes, index=1 if len(lista_meses) > 0 else 0)

        # 4. Aplicação do Filtro
        if mes_selecionado != "Todos":
            df_exibir_kpi = df_fin[df_fin['Mes_Ano'] == mes_selecionado].copy()
        else:
            df_exibir_kpi = df_fin.copy()

        # --- CÁLCULOS (USANDO O DATAFRAME FILTRADO) ---
        df_realizado = df_exibir_kpi[df_exibir_kpi['Status'] == 'Pago']
        entradas = df_realizado[df_realizado['Tipo'] == 'Entrada']['Valor_Num'].sum()
        saidas = df_realizado[df_realizado['Tipo'] == 'Saída']['Valor_Num'].sum()
        saldo = entradas - saidas
        
        # Formatação Visual
        def fmt(v): return f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        c1, c2, c3 = st.columns(3)
        # Exibe qual mês está sendo mostrado no título dos cards (opcional, mas ajuda)
        sufixo = f" ({mes_selecionado})" if mes_selecionado != "Todos" else " (Geral)"
        
        c1.metric(f"Entradas{sufixo}", fmt(entradas))
        c2.metric(f"Saídas{sufixo}", fmt(saidas))
        c3.metric("Saldo Líquido", fmt(saldo), delta_color="normal")
        
        st.subheader("Extrato")
        
        # Preparação para Tabela
        df_tabela = df_exibir_kpi.copy()
        
        # Ordena por data (mais recente primeiro)
        df_tabela = df_tabela.sort_values(by='Data_Dt', ascending=False)
        
        try:
             df_tabela['Valor'] = df_tabela['Valor_Num'].apply(fmt)
        except: pass

        cols = ['Data', 'Tipo', 'Categoria', 'Descrição', 'Valor', 'Status']
        validas = [c for c in cols if c in df_tabela.columns]

        def color_tipo(val):
            return f'color: {"red" if val == "Saída" else "green"}'

        st.dataframe(
            df_tabela[validas].style.map(color_tipo, subset=['Tipo']),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhum lançamento financeiro registrado.")