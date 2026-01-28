import streamlit as st
import database as db
from datetime import date

def form_renovacao_pacote():
    st.markdown("#### Cadastro de Aulas")
    
    df_alunos = db.get_alunos()
    if df_alunos.empty:
        st.warning("Nenhum aluno cadastrado no sistema.")
        return

    # Mapeia Nome -> ID com segurança nas colunas novas
    col_nome = 'Nome Aluno' if 'Nome Aluno' in df_alunos.columns else 'nome_aluno'
    col_id = 'ID Aluno' if 'ID Aluno' in df_alunos.columns else 'id_aluno'
    
    try:
        mapa_alunos = dict(zip(df_alunos[col_nome], df_alunos[col_id]))
    except KeyError:
        st.error("Erro nas colunas do arquivo CAD_Alunos.")
        return

    with st.form("form_venda_avulsa", clear_on_submit=True, enter_to_submit=False):
        col_sel, col_hr = st.columns([2, 1])
        with col_sel:
            nome_sel = st.selectbox("Selecione o Aluno", options=df_alunos[col_nome].unique())
        with col_hr:
            qtd_horas = st.number_input("Qtd Horas", min_value=1, step=1)
            
        c1, c2, c3 = st.columns(3)
        data_contrato = c1.date_input("Data Venda", format="DD/MM/YYYY")
        pagou = c2.checkbox("Pagamento confirmado?", value=True)
        dt_pag = c3.date_input("Data Pagamento", value=date.today(), format="DD/MM/YYYY") if pagou else None

        if st.form_submit_button("✅ Confirmar Venda"):
            id_aluno = mapa_alunos[nome_sel]
            contrato_str = data_contrato.strftime("%d/%m/%Y")
            pag_str = dt_pag.strftime("%d/%m/%Y") if dt_pag else ""
            
            sucesso, msg = db.registrar_venda_automatica(id_aluno, nome_sel, qtd_horas, "Pix", contrato_str, pag_str)
            
            if sucesso:
                st.success(msg)
                st.cache_data.clear() # Limpa cache para atualizar saldos imediatamente
            else:
                st.error(msg)