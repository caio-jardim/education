import streamlit as st
import database as db
from datetime import date
import pandas as pd

def show_financeiro():
    st.markdown("### 💸 Fluxo de Caixa Geral")
    
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
    
    df_fin = db.get_financeiro_geral()
    
    if not df_fin.empty:
        # --- NOVA LÓGICA DE LEITURA ---
        # Como agora salvamos números, basta converter com to_numeric
        # Ele lida automaticamente com ints e floats que o Sheets mandar
        df_fin['Valor_Num'] = pd.to_numeric(df_fin['Valor'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)
        
        # Filtros
        df_realizado = df_fin[df_fin['Status'] == 'Pago']
        entradas = df_realizado[df_realizado['Tipo'] == 'Entrada']['Valor_Num'].sum()
        saidas = df_realizado[df_realizado['Tipo'] == 'Saída']['Valor_Num'].sum()
        saldo = entradas - saidas
        
        # Formatação Visual (Para ficar bonito na tela com vírgula)
        def fmt(v): return f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas (Pago)", fmt(entradas))
        c2.metric("Saídas (Pago)", fmt(saidas))
        c3.metric("Saldo", fmt(saldo), delta_color="normal")
        
        st.subheader("Extrato")
        
        # Na tabela, também formatamos para visualização
        df_exibicao = df_fin.copy()
        try:
             df_exibicao['Valor'] = df_exibicao['Valor_Num'].apply(fmt)
        except: pass

        cols = ['Data', 'Tipo', 'Categoria', 'Descrição', 'Valor', 'Status']
        validas = [c for c in cols if c in df_exibicao.columns]

        def color_tipo(val):
            return f'color: {"red" if val == "Saída" else "green"}'

        st.dataframe(
            df_exibicao[validas].style.map(color_tipo, subset=['Tipo']),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhum lançamento.")