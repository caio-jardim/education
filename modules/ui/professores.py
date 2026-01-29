import streamlit as st
import database as db
import pandas as pd
from modules.ui import core  # <--- Padronização de notificações

# --- FUNÇÃO 1: USADA NA PÁGINA 'CADASTROS' (CRIAÇÃO) ---
def form_novo_professor():
    # --- CSS ESPECÍFICO (LAYOUT) ---
    # Igual ao do alunos.py: formulário transparente e ajuste de margem superior
    st.markdown("""
        <style>
            div[data-testid="stForm"] {
                border: none !important;
                box-shadow: none !important;
                background-color: transparent !important;
                padding: 0px !important;
            }
            div[data-testid="stForm"] > div:first-child {
                padding-top: 0px !important;
                margin-top: -20px !important; 
            }
        </style>
    """, unsafe_allow_html=True)

    with st.form("form_prof_new", clear_on_submit=True, enter_to_submit=False):
        
        # --- CABEÇALHO (Novo Professor) ---
        c_icon, c_title = st.columns([0.5, 10])
        with c_icon:
            # Assumindo icon_novo_professor.png para manter padrão com icon_novo_aluno.png
            # Se não tiver, o Streamlit mostra um 'broken image' discreto ou você pode usar outro.
            st.image("assets/icon_novo_professor.png", width=45)
        with c_title:
            st.markdown("### Novo Professor")

        # --- CAMPOS PESSOAIS ---
        nome = st.text_input("Nome Completo")
        
        c1, c2, c3 = st.columns(3)
        v1 = c1.number_input("R$/h Education", min_value=0.0, step=1.0, format="%.2f")
        v2 = c2.number_input("R$/h Online", min_value=0.0, step=1.0, format="%.2f")
        v3 = c3.number_input("R$/h Casa", min_value=0.0, step=1.0, format="%.2f")
        
        st.markdown("<br>", unsafe_allow_html=True)

        # --- SEÇÃO DADOS DE ACESSO (Com ícone Cadeado) ---
        c_icon_lock, c_title_lock = st.columns([0.5, 10])
        with c_icon_lock:
            st.image("assets/icon_cadeado.png", width=45)
        with c_title_lock:
            st.markdown("### Dados de Acesso")
            # st.caption("Credenciais para login no sistema.")
        
        col_u1, col_u2, col_u3 = st.columns(3)
        user_login = col_u1.text_input("Username (Login)")
        user_pass = col_u2.text_input("Password (Senha)", type="password")
        user_perfil = col_u3.selectbox("Tipo Perfil", ["prof", "estagiario", "admin"])
        
        st.markdown("<br>", unsafe_allow_html=True)

        # --- BOTÕES DE AÇÃO (Lado a Lado) ---
        c_btn_save, c_btn_cancel, c_void = st.columns([1.5, 1.5, 6])
        
        with c_btn_save:
            submit = st.form_submit_button("Salvar Cadastro")
        
        with c_btn_cancel:
            cancel = st.form_submit_button("Cancelar", type="secondary")

        if cancel:
            st.rerun()

        if submit:
            if not nome: 
                core.notify_warning("Nome obrigatório!")
            elif not user_login or not user_pass: 
                core.notify_warning("Login e Senha são obrigatórios!")
            else:
                try:
                    # Chama função do DB
                    sucesso, msg = db.cadastrar_professor(nome, v1, v2, v3, True, user_login, user_pass, user_perfil)
                    
                    if sucesso: 
                        core.notify_success(msg)
                        import time
                        time.sleep(1)
                        st.rerun()
                    else: 
                        core.notify_error(msg)
                        
                except Exception as e: 
                    core.notify_error(f"Erro técnico: {e}")


# --- FUNÇÃO 2: USADA NA NOVA PÁGINA 'PROFESSORES' (GESTÃO) ---
def show_gestao_vinculos():
    st.markdown("### 👨‍🏫 Professores & Alunos")
    
    # Removido CSS manual do Toast daqui (já está no core.py)

    # 1. Carregar Dados
    df_profs = db.get_professores()
    df_alunos = db.get_alunos()
    df_links = db.get_vinculos()
    
    # Filtra apenas professores ativos
    if not df_profs.empty and 'Status' in df_profs.columns:
        df_profs = df_profs[df_profs['Status'] == 'Ativo']

    if df_profs.empty or df_alunos.empty:
        st.warning("É necessário ter professores e alunos cadastrados.")
        return

    # Dicionários Auxiliares
    mapa_profs = {row['Nome Professor']: str(row['ID Professor']) for _, row in df_profs.iterrows()}
    mapa_alunos_nome_id = {row['Nome Aluno']: str(row['ID Aluno']) for _, row in df_alunos.iterrows()}
    mapa_alunos_id_nome = {str(row['ID Aluno']): row['Nome Aluno'] for _, row in df_alunos.iterrows()}
    
    # --- INTERFACE ---
    col_sel, col_info = st.columns([1, 2])
    
    with col_sel:
        nome_prof_sel = st.selectbox("Selecione o Professor", list(mapa_profs.keys()))
    
    if nome_prof_sel:
        id_prof_sel = mapa_profs[nome_prof_sel]
        
        # Descobre alunos atuais desse professor
        alunos_ja_vinculados = []
        if not df_links.empty:
            links_prof = df_links[df_links['ID Professor'].astype(str) == id_prof_sel]
            ids_alunos = links_prof['ID Aluno'].astype(str).tolist()
            alunos_ja_vinculados = [mapa_alunos_id_nome[uid] for uid in ids_alunos if uid in mapa_alunos_id_nome]
        
        with col_info:
            with st.container(border=True):
                st.markdown(f"**Alunos atendidos por:** {nome_prof_sel}")
                
                with st.form("form_update_vinculos"):
                    alunos_selecionados = st.multiselect(
                        "Lista de Alunos:",
                        options=list(mapa_alunos_nome_id.keys()),
                        default=alunos_ja_vinculados
                    )
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("💾 Atualizar Carteira de Alunos", use_container_width=True):
                        ids_para_salvar = [mapa_alunos_nome_id[nome] for nome in alunos_selecionados]
                        try:
                            sucesso, msg = db.salvar_vinculos_do_professor(id_prof_sel, ids_para_salvar)
                            if sucesso: core.notify_success(msg)
                            else: core.notify_error("Erro ao salvar.")
                        except Exception as e: core.notify_error(f"Erro: {e}")