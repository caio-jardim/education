import streamlit as st
import database as db
from datetime import date, datetime
import pandas as pd

def show_financeiro():
    st.markdown("### 💸 Fluxo de Caixa")
    
    # --- 1. CARREGA ALUNOS PARA O FORMULÁRIO ---
    df_alunos = db.get_alunos()
    mapa_alunos = {}
    if not df_alunos.empty:
        # Tenta pegar as colunas certas
        col_nome = 'Nome Aluno' if 'Nome Aluno' in df_alunos.columns else 'nome_aluno'
        col_id = 'ID Aluno' if 'ID Aluno' in df_alunos.columns else 'id_aluno'
        if col_nome in df_alunos.columns:
            mapa_alunos = dict(zip(df_alunos[col_nome], df_alunos[col_id]))
    
    lista_alunos_opcoes = ["- Sem Aluno Vinculado -"] + list(mapa_alunos.keys())

    # --- 2. FORMULÁRIO DE LANÇAMENTO ---
    with st.expander("➕ Novo Lançamento", expanded=False):
        with st.form("form_financeiro_geral", clear_on_submit=True, enter_to_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                tipo = st.radio("Tipo", ["Saída (Despesa)", "Entrada (Receita)"], horizontal=True)
                if "Saída" in tipo: cats = ["Pagamento Professores", "Salários", "Aluguel", "Software", "Marketing", "Outros"]
                else: cats = ["Venda Pacote", "Mensalidade", "Aporte", "Outros"]
                categoria = st.selectbox("Categoria", cats)
                descricao = st.text_input("Descrição", placeholder="Ex: Pagamento Mensalidade Fevereiro")

            with c2:
                valor = st.number_input("Valor (R$)", min_value=0.01, step=10.00, format="%.2f")
                data_mov = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
                
                # NOVO CAMPO: SELEÇÃO DE ALUNO
                aluno_selecionado = st.selectbox("Aluno (Opcional)", options=lista_alunos_opcoes)
                
                pago = st.checkbox("Pago/Recebido?", value=True)
                status = "Pago" if pago else "Pendente"

            if st.form_submit_button("💾 Registrar"):
                if not descricao: st.error("Descrição obrigatória.")
                else:
                    try:
                        data_str = data_mov.strftime("%d/%m/%Y")
                        tipo_final = "Saída" if "Saída" in tipo else "Entrada"
                        
                        # Resolve ID e Nome do Aluno
                        id_aluno_save = ""
                        nome_aluno_save = ""
                        if aluno_selecionado != "- Sem Aluno Vinculado -":
                            nome_aluno_save = aluno_selecionado
                            id_aluno_save = mapa_alunos.get(aluno_selecionado, "")

                        # Chama a função atualizada no database
                        db.registrar_movimentacao_financeira(
                            data_str, 
                            tipo_final, 
                            categoria, 
                            descricao, 
                            valor, 
                            status,
                            id_aluno_save,  # Novo
                            nome_aluno_save # Novo
                        )
                        st.success(f"Salvo: R$ {valor:.2f}")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e: st.error(f"Erro: {e}")

    st.divider()
    
    # --- 3. CARREGAMENTO E FILTRO ---
    df_fin = db.get_financeiro_geral()
    
    if not df_fin.empty:
        # Tratamento numérico
        df_fin['Valor_Num'] = pd.to_numeric(df_fin['Valor'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)
        
        # Tratamento de Data
        df_fin['Data_Dt'] = pd.to_datetime(df_fin['Data'], format="%d/%m/%Y", errors='coerce')
        df_fin['Mes_Ano'] = df_fin['Data_Dt'].dt.strftime("%m/%Y")
        
        # Filtro de Mês
        lista_meses = sorted(df_fin['Mes_Ano'].dropna().unique(), key=lambda x: datetime.strptime(x, "%m/%Y"), reverse=True)
        lista_opcoes = ["Todos"] + list(lista_meses)
        
        col_filtro, col_vazio = st.columns([1, 3])
        with col_filtro:
            mes_selecionado = st.selectbox("📅 Filtrar Mês", options=lista_opcoes, index=1 if len(lista_meses) > 0 else 0)

        if mes_selecionado != "Todos":
            df_exibir_kpi = df_fin[df_fin['Mes_Ano'] == mes_selecionado].copy()
        else:
            df_exibir_kpi = df_fin.copy()

        # Cálculos
        df_realizado = df_exibir_kpi[df_exibir_kpi['Status'] == 'Pago']
        entradas = df_realizado[df_realizado['Tipo'] == 'Entrada']['Valor_Num'].sum()
        saidas = df_realizado[df_realizado['Tipo'] == 'Saída']['Valor_Num'].sum()
        saldo = entradas - saidas
        
        def fmt(v): return f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        c1, c2, c3 = st.columns(3)
        sufixo = f" ({mes_selecionado})" if mes_selecionado != "Todos" else " (Geral)"
        c1.metric(f"Entradas{sufixo}", fmt(entradas))
        c2.metric(f"Saídas{sufixo}", fmt(saidas))
        c3.metric("Saldo Líquido", fmt(saldo), delta_color="normal")
        
        st.subheader("Extrato")
        
        df_tabela = df_exibir_kpi.copy()
        df_tabela = df_tabela.sort_values(by='Data_Dt', ascending=False)
        
        try: df_tabela['Valor'] = df_tabela['Valor_Num'].apply(fmt)
        except: pass

        # --- 4. COLUNAS DA TABELA (COM ALUNO AGORA) ---
        # Adicionei 'Nome Aluno' na lista de colunas para exibir
        cols = ['Data', 'Tipo', 'Categoria', 'Descrição', 'Valor', 'Status', 'Nome Aluno']
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