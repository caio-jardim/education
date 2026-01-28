# modules/forms.py
import streamlit as st
import database as db
from datetime import date
import re

# --- FORMULÁRIO 1: NOVO ALUNO (COM PACOTE INICIAL) ---
def form_novo_aluno():
    st.markdown("#### 🚀 Cadastro de Novo Aluno")
    
    if 'reset_counter_aluno' not in st.session_state: st.session_state['reset_counter_aluno'] = 0
    c_id = st.session_state['reset_counter_aluno']

    # Carrega Professores
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

    with st.form(key=f"form_cadastro_aluno_{c_id}"):
        st.info("Preencha os dados cadastrais e o primeiro pacote contratado.")
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
            
            profs_selecionados = st.multiselect("Professores Preferenciais", options=opcoes_nomes_profs, placeholder="Selecione (opcional)")
            
            escola = st.text_input("Escola")
            endereco = st.text_input("Endereço")
        
        obs = st.text_area("Observações")
        
        st.markdown("---")
        st.markdown("##### 📦 Primeiro Pacote")
        c1, c2, c3 = st.columns(3)
        qtd_horas = c1.number_input("Qtd Horas", min_value=1, step=1)
        data_contrato = c2.date_input("Data Contratação", format="DD/MM/YYYY")
        
        pagou_agora = c3.checkbox("Já pagou?", value=True)
        data_pagamento = st.date_input("Data Pagamento", value=date.today(), format="DD/MM/YYYY") if pagou_agora else None
        
        if st.form_submit_button("💾 Salvar Novo Aluno"):
            if not nome: st.error("Nome obrigatório"); return
            
            try:
                nasc_str = nascimento.strftime("%d/%m/%Y") if nascimento else ""
                contrato_str = data_contrato.strftime("%d/%m/%Y")
                pagamento_str = data_pagamento.strftime("%d/%m/%Y") if data_pagamento else ""
                
                # 1. Cadastra
                novo_id = db.cadastrar_aluno(nome, responsavel, telefone, nasc_str, serie, escola, endereco, obs)
                
                # 2. Vincula
                ids_vincular = [mapa_professores[p] for p in profs_selecionados]
                db.salvar_vinculos_professor(novo_id, ids_vincular)
                
                # 3. Vende
                sucesso, msg = db.registrar_venda_automatica(novo_id, nome, qtd_horas, "Pix", contrato_str, pagamento_str)
                
                if sucesso:
                    st.success(f"Aluno {nome} criado! {msg}")
                    st.session_state['reset_counter_aluno'] += 1
                    st.rerun()
                else:
                    st.warning(f"Aluno criado, erro na venda: {msg}")
            except Exception as e:
                st.error(f"Erro: {e}")

# --- FORMULÁRIO 2: RENOVAÇÃO / VENDA PARA ALUNO JÁ CADASTRADO ---
def form_renovacao_pacote():
    st.markdown("#### 💰 Renovação de Pacote / Venda Avulsa")
    st.info("Utilize este módulo para alunos que JÁ estão cadastrados no sistema.")
    
    df_alunos = db.get_alunos()
    if df_alunos.empty:
        st.warning("Sem alunos cadastrados.")
        return

    # Mapeamento seguro
    col_nome = 'Nome Aluno' if 'Nome Aluno' in df_alunos.columns else 'nome_aluno'
    col_id = 'ID Aluno' if 'ID Aluno' in df_alunos.columns else 'id_aluno'
    mapa_alunos = dict(zip(df_alunos[col_nome], df_alunos[col_id]))

    with st.form("form_renovacao"):
        nome_sel = st.selectbox("Selecione o Aluno", options=df_alunos[col_nome].unique())
        
        c1, c2, c3 = st.columns(3)
        qtd_horas = c1.number_input("Qtd Horas do Novo Pacote", min_value=1, step=1)
        data_contrato = c2.date_input("Data da Renovação", format="DD/MM/YYYY")
        
        pagou = c3.checkbox("Pagamento confirmado?", value=True)
        dt_pag = st.date_input("Data do Pagamento", value=date.today(), format="DD/MM/YYYY") if pagou else None

        if st.form_submit_button("✅ Confirmar Renovação"):
            id_aluno = mapa_alunos[nome_sel]
            contrato_str = data_contrato.strftime("%d/%m/%Y")
            pag_str = dt_pag.strftime("%d/%m/%Y") if dt_pag else ""
            
            sucesso, msg = db.registrar_venda_automatica(id_aluno, nome_sel, qtd_horas, "Pix", contrato_str, pag_str)
            if sucesso:
                st.success(msg)
                st.cache_data.clear() # Limpa cache para atualizar saldos
            else:
                st.error(msg)

# --- FORMULÁRIO 3: NOVO PROFESSOR ---
def form_novo_professor():
    st.markdown("#### 👨‍🏫 Cadastro de Professor")
    with st.form("form_prof"):
        nome = st.text_input("Nome Completo")
        c1, c2, c3 = st.columns(3)
        v1 = c1.number_input("R$/h Education")
        v2 = c2.number_input("R$/h Online")
        v3 = c3.number_input("R$/h Casa")
        
        if st.form_submit_button("Salvar Professor"):
            if nome:
                db.cadastrar_professor(nome, v1, v2, v3)
                st.success("Professor cadastrado!")
                st.rerun()