import streamlit as st
import database as db
from datetime import date
import re

def form_novo_aluno():
    st.markdown("#### Cadastro de Novo Aluno")
    
    if 'reset_counter_aluno' not in st.session_state: st.session_state['reset_counter_aluno'] = 0
    c_id = st.session_state['reset_counter_aluno']

    # 1. Carrega Professores para o Multiselect
    df_profs = db.get_professores()
    mapa_professores = {}
    opcoes_nomes_profs = []
    
    if not df_profs.empty:
        col_nome = 'Nome Professor' if 'Nome Professor' in df_profs.columns else 'nome_professor'
        col_id = 'ID Professor' if 'ID Professor' in df_profs.columns else 'id_prof'
        try:
            mapa_professores = dict(zip(df_profs[col_nome], df_profs[col_id]))
            opcoes_nomes_profs = list(mapa_professores.keys())
        except: pass

    # 2. O Formulário
    with st.form(key=f"form_cadastro_aluno_{c_id}", clear_on_submit=True, enter_to_submit=False):
        col_a, col_b = st.columns(2)
        with col_a:
            nome = st.text_input("Nome do Aluno")
            responsavel = st.text_input("Nome do Responsável")
            telefone = st.text_input("Telefone", placeholder="61999999999")
            tem_nasc = st.checkbox("Informar Nascimento?", value=True)
            nascimento = st.date_input("Data Nascimento", min_value=date(1920, 1, 1), max_value=date.today(), format="DD/MM/YYYY") if tem_nasc else None

        with col_b:
            opcoes_series = ["Selecione...", "Infantil", "1º Ano Fund.", "2º Ano Fund.", "3º Ano Fund.", "4º Ano Fund.", "5º Ano Fund.", "6º Ano Fund.", "7º Ano Fund.", "8º Ano Fund.", "9º Ano Fund.", "1º Ano Ens. Médio", "2º Ano Ens. Médio", "3º Ano Ens. Médio", "Pré-Vestibular", "Outros"]
            serie = st.selectbox("Série/Ano", options=opcoes_series)
            
            # Multiselect de Professores
            profs_selecionados = st.multiselect("Professores Preferenciais", options=opcoes_nomes_profs, placeholder="Selecione (opcional)")
            
            escola = st.text_input("Escola")
            endereco = st.text_input("Endereço")
        
        obs = st.text_area("Observações")
        
        st.markdown("---")
        st.markdown("##### Primeiro Pacote")
        c1, c2, c3 = st.columns(3)
        qtd_horas = c1.number_input("Qtd Horas", min_value=1, step=1)
        data_contrato = c2.date_input("Data Contratação", format="DD/MM/YYYY")
        
        pagou_agora = c3.checkbox("Já pagou?", value=True)
        data_pagamento = st.date_input("Data Pagamento", value=date.today(), format="DD/MM/YYYY") if pagou_agora else None
        
        if st.form_submit_button("💾 Salvar Novo Aluno"):
            if not nome: st.error("Nome obrigatório"); return
            
            try:
                # Formatações
                nasc_str = nascimento.strftime("%d/%m/%Y") if nascimento else ""
                contrato_str = data_contrato.strftime("%d/%m/%Y")
                pagamento_str = data_pagamento.strftime("%d/%m/%Y") if data_pagamento else ""
                
                # A. Salva Aluno
                novo_id = db.cadastrar_aluno(nome, responsavel, telefone, nasc_str, serie, escola, endereco, obs)
                
                # B. Salva Vínculos
                ids_vincular = [mapa_professores[p] for p in profs_selecionados]
                db.salvar_vinculos_professor(novo_id, ids_vincular)
                
                # C. Salva Venda
                sucesso, msg = db.registrar_venda_automatica(novo_id, nome, qtd_horas, "Pix", contrato_str, pagamento_str)
                
                if sucesso:
                    st.success(f"Aluno {nome} criado! {msg}")
                    st.session_state['reset_counter_aluno'] += 1
                    st.rerun()
                else:
                    st.warning(f"Aluno criado, mas houve erro na venda: {msg}")
            except Exception as e:
                st.error(f"Erro técnico: {e}")