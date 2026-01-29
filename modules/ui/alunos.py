import streamlit as st
import database as db
from datetime import date
import re
from modules.ui import core

def form_novo_aluno():
    # --- CSS ESPECÍFICO DESTA TELA (LAYOUT APENAS) ---
    # Note que removi a parte do "ToastContainer" daqui, pois já está no core.py global.
    # Mantivemos apenas o que deixa o formulário transparente e ajusta o título.
    st.markdown("""
        <style>
            /* 1. Formulário Transparente (Sem borda e sem fundo preto) */
            div[data-testid="stForm"] {
                border: none !important;
                box-shadow: none !important;
                background-color: transparent !important;
                padding: 0px !important;
            }
            /* 2. REDUÇÃO DE ESPAÇO DO TÍTULO */
            /* Puxa o primeiro bloco do formulário para cima, colando nas abas */
            div[data-testid="stForm"] > div:first-child {
                padding-top: 0px !important;
                margin-top: -20px !important; 
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Contador para reset
    if 'reset_counter_aluno' not in st.session_state: st.session_state['reset_counter_aluno'] = 0
    c_id = st.session_state['reset_counter_aluno']

    # Carrega Professores
    df_profs = db.get_professores()
    mapa_professores = {}
    opcoes_nomes_profs = []
    
    if not df_profs.empty:
        col_nome = 'Nome Professor' if 'Nome Professor' in df_profs.columns else 'nome_professor'
        cols_possiveis_id = ['ID Professor', 'ID', 'id_prof']
        col_id = next((c for c in cols_possiveis_id if c in df_profs.columns), None)

        if col_id and col_nome:
            try:
                mapa_professores = dict(zip(df_profs[col_nome], df_profs[col_id]))
                opcoes_nomes_profs = list(mapa_professores.keys())
            except: pass

    # --- INÍCIO DO FORMULÁRIO ---
    with st.form(key=f"form_cadastro_aluno_{c_id}", clear_on_submit=True, enter_to_submit=False):
        
        # Ícone e Título
        c_icon, c_title = st.columns([0.5, 10])
        with c_icon:
            st.image("assets/icon_novo_aluno.png", width=45) 
        with c_title:
            st.markdown("### Novo Aluno")
            st.caption("Preencha os dados pessoais e escolares.")

        # Campos
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
        
        st.markdown("<br>", unsafe_allow_html=True)

        # Seção Pacote
        c_icon2, c_title2 = st.columns([0.5, 10])
        with c_icon2:
             st.image("assets/icon_novo_pacote.png", width=45)
        with c_title2:
            st.markdown("### Primeiro Pacote")
        
        c1, c2, c3 = st.columns(3)
        qtd_horas = c1.number_input("Qtd Horas", min_value=1.0, step=0.5, format="%.1f")
        data_contrato = c2.date_input("Data Contratação", format="DD/MM/YYYY")
        pagou_agora = c3.checkbox("Já pagou?", value=True)
        data_pagamento = st.date_input("Data Pagamento", value=date.today(), format="DD/MM/YYYY") if pagou_agora else None
        
        st.markdown("<br>", unsafe_allow_html=True)

        # --- BOTÕES DE AÇÃO ---
        c_btn_save, c_btn_cancel, c_void = st.columns([1.5, 1.5, 6])
        
        with c_btn_save:
            submit = st.form_submit_button("Salvar Cadastro")
        
        with c_btn_cancel:
            cancel = st.form_submit_button("Cancelar", type="secondary")

        if cancel:
            st.rerun()

        if submit:
            if not nome: 
                # 2. SUBSTITUIÇÃO: core.notify_warning
                core.notify_warning("Nome obrigatório")
            else:
                try:
                    # Formatações
                    nasc_str = nascimento.strftime("%d/%m/%Y") if nascimento else ""
                    contrato_str = data_contrato.strftime("%d/%m/%Y")
                    pagamento_str = data_pagamento.strftime("%d/%m/%Y") if data_pagamento else ""
                    
                    # Salvar
                    novo_id = db.cadastrar_aluno(nome, responsavel, telefone, nasc_str, serie, escola, endereco, obs)
                    
                    ids_vincular = [mapa_professores[p] for p in profs_selecionados]
                    if ids_vincular:
                        db.salvar_vinculos_do_professor(novo_id, ids_vincular)
                    
                    sucesso, msg = db.registrar_venda_automatica(novo_id, nome, qtd_horas, "Pix", contrato_str, pagamento_str)
                    
                    if sucesso:
                        # 3. SUBSTITUIÇÃO: core.notify_success
                        core.notify_success(f"Aluno {nome} criado!")
                        st.session_state['reset_counter_aluno'] += 1
                        
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        # 4. SUBSTITUIÇÃO: core.notify_warning (ou error)
                        core.notify_warning(f"Erro na venda: {msg}")
                        
                except Exception as e:
                    # 5. SUBSTITUIÇÃO: core.notify_error
                    core.notify_error(f"Erro técnico: {e}")

def show_gestao_vinculos():
    st.markdown("### 🎓 Alunos & Professores")
    
    # CSS Toast
    st.markdown("""<style>div[data-testid="stToastContainer"] {top: 80px; right: 20px; bottom: unset; left: unset; align-items: flex-end;}</style>""", unsafe_allow_html=True)

    # 1. Carregar Dados
    df_alunos = db.get_alunos()
    df_profs = db.get_professores()
    df_links = db.get_vinculos()
    
    # Filtra profs ativos
    if not df_profs.empty and 'Status' in df_profs.columns:
        df_profs = df_profs[df_profs['Status'] == 'Ativo']

    if df_alunos.empty or df_profs.empty:
        st.warning("Necessário cadastrar alunos e professores antes.")
        return

    # Mapeamentos
    mapa_alunos = {row['Nome Aluno']: str(row['ID Aluno']) for _, row in df_alunos.iterrows()}
    mapa_profs_nome_id = {row['Nome Professor']: str(row['ID Professor']) for _, row in df_profs.iterrows()}
    mapa_profs_id_nome = {str(row['ID Professor']): row['Nome Professor'] for _, row in df_profs.iterrows()}

    # Interface
    col_sel, col_info = st.columns([1, 2])
    
    with col_sel:
        nome_aluno_sel = st.selectbox("Selecione o Aluno", list(mapa_alunos.keys()))
    
    if nome_aluno_sel:
        id_aluno_sel = mapa_alunos[nome_aluno_sel]
        
        # Descobre profs atuais desse aluno
        profs_ja_vinculados = []
        if not df_links.empty:
            # Filtra por ID Aluno
            links_aluno = df_links[df_links['ID Aluno'].astype(str) == id_aluno_sel]
            ids_profs = links_aluno['ID Professor'].astype(str).tolist()
            # Converte IDs para Nomes
            profs_ja_vinculados = [mapa_profs_id_nome[uid] for uid in ids_profs if uid in mapa_profs_id_nome]
            
        with col_info:
            with st.container(border=True):
                st.markdown(f"**Professores de:** {nome_aluno_sel}")
                
                with st.form("form_update_vinculos_aluno"):
                    profs_selecionados = st.multiselect(
                        "Lista de Professores:",
                        options=list(mapa_profs_nome_id.keys()),
                        default=profs_ja_vinculados
                    )
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("💾 Atualizar Equipe do Aluno", use_container_width=True):
                        # Converte Nomes para IDs
                        ids_para_salvar = [mapa_profs_nome_id[nome] for nome in profs_selecionados]
                        
                        try:
                            # Chama a nova função do DB
                            sucesso, msg = db.salvar_vinculos_do_aluno(id_aluno_sel, ids_para_salvar)
                            if sucesso: st.toast(msg, icon='✅')
                            else: st.toast("Erro ao salvar.", icon='❌')
                        except Exception as e:
                            st.toast(f"Erro: {e}", icon='🔥')