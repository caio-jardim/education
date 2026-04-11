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
    from datetime import datetime

    # CSS para cards de métricas do professor
    st.markdown("""
        <style>
            .prof-metric-card {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 16px 20px;
                border-left: 4px solid #C5A065;
            }
            .prof-metric-label {
                color: #757575;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                margin-bottom: 4px;
            }
            .prof-metric-value {
                color: #1A1A1A;
                font-size: 24px;
                font-weight: 700;
                font-family: 'Poppins', sans-serif;
            }
        </style>
    """, unsafe_allow_html=True)

    # Header com ícone
    c_icon, c_title = st.columns([0.5, 10])
    with c_icon:
        st.image("assets/icon_novo_professor.png", width=45)
    with c_title:
        st.markdown("### Professores")

    # 1. Carregar Dados
    with st.spinner("Carregando dados..."):
        df_profs = db.get_professores()
        df_alunos = db.get_alunos()
        df_links = db.get_vinculos()
        df_aulas = db.get_aulas()

    if not df_profs.empty and 'Status' in df_profs.columns:
        df_profs = df_profs[df_profs['Status'] == 'Ativo']

    if df_profs.empty:
        st.info("Nenhum professor ativo cadastrado.")
        return

    # Dicionários Auxiliares
    mapa_profs = {row['Nome Professor']: str(row['ID Professor']) for _, row in df_profs.iterrows()}
    mapa_alunos_nome_id = {}
    mapa_alunos_id_nome = {}
    if not df_alunos.empty:
        mapa_alunos_nome_id = {row['Nome Aluno']: str(row['ID Aluno']) for _, row in df_alunos.iterrows()}
        mapa_alunos_id_nome = {str(row['ID Aluno']): row['Nome Aluno'] for _, row in df_alunos.iterrows()}

    # 2. Filtro de Professor
    nome_prof_sel = st.selectbox(
        "Selecione o Professor",
        options=list(mapa_profs.keys()),
        key="filtro_prof_gestao"
    )

    if not nome_prof_sel:
        return

    id_prof_sel = mapa_profs[nome_prof_sel]

    # 3. Preparar dados de aulas do professor
    meses_pt = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    meses_pt_inv = {v: k for k, v in meses_pt.items()}

    hoje = datetime.now()
    mes_label_atual = f"{meses_pt[hoje.month]}/{hoje.year}"

    df_aulas_prof = pd.DataFrame()
    opcoes_meses = [mes_label_atual]

    if not df_aulas.empty:
        df_tmp = df_aulas.copy()
        df_tmp['Data_Dt'] = pd.to_datetime(df_tmp['Data'], format="%d/%m/%Y", errors='coerce')
        df_aulas_prof = df_tmp[df_tmp['ID Professor'].astype(str) == id_prof_sel].copy()

        if not df_aulas_prof.empty:
            df_aulas_prof['Mes_Filtro'] = df_aulas_prof['Data_Dt'].apply(
                lambda x: f"{meses_pt[x.month]}/{x.year}" if pd.notna(x) else None
            )
            meses_raw = df_aulas_prof['Mes_Filtro'].dropna().unique().tolist()

            def _sort_mes(label):
                parts = label.split('/')
                mes_num = meses_pt_inv.get(parts[0], 1)
                ano = int(parts[1]) if len(parts) > 1 else hoje.year
                return (ano, mes_num)

            opcoes_meses = sorted(meses_raw, key=_sort_mes, reverse=True)
            if not opcoes_meses:
                opcoes_meses = [mes_label_atual]

    # Seletor de Período
    idx_default = 0
    if mes_label_atual in opcoes_meses:
        idx_default = opcoes_meses.index(mes_label_atual)

    col_filtro_mes, _ = st.columns([1, 2])
    with col_filtro_mes:
        mes_selecionado = st.selectbox(
            "Período",
            options=opcoes_meses,
            index=idx_default,
            key="filtro_mes_prof"
        )

    # 4. Filtrar aulas do mês selecionado
    comissao_mes = 0.0
    total_aulas_mes = 0
    df_aulas_mes = pd.DataFrame()

    def _parse_comissao(v):
        try:
            s = str(v).replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(s) if s else 0.0
        except:
            return 0.0

    if not df_aulas_prof.empty:
        df_aulas_mes = df_aulas_prof[df_aulas_prof['Mes_Filtro'] == mes_selecionado].copy()
        total_aulas_mes = len(df_aulas_mes)

        # Detecta coluna de comissão (pode ser 'Comissão' ou 'Comissão Professor')
        col_comissao = None
        for c in df_aulas_mes.columns:
            if 'comissão' in c.lower() or 'comissao' in c.lower():
                col_comissao = c
                break

        if not df_aulas_mes.empty and col_comissao:
            df_realizadas = df_aulas_mes[df_aulas_mes['Status'] == 'Realizada']
            comissao_mes = df_realizadas[col_comissao].apply(_parse_comissao).sum()

    # 5. Cards de Métricas
    def _fmt_brl(valor):
        try:
            valor_num = float(valor) if isinstance(valor, str) else float(valor)
        except (ValueError, TypeError):
            valor_num = 0.0
        formatted = f"{valor_num:,.2f}"
        return "R$ " + formatted.replace(',', 'X').replace('.', ',').replace('X', '.')

    st.markdown("")
    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.markdown(f"""
            <div class="prof-metric-card">
                <div class="prof-metric-label">Comissão do Mês</div>
                <div class="prof-metric-value">{_fmt_brl(comissao_mes)}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown(f"""
            <div class="prof-metric-card">
                <div class="prof-metric-label">Aulas no Mês</div>
                <div class="prof-metric-value">{total_aulas_mes}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # 6. Tabela de Aulas Ministradas
    st.markdown("##### Aulas Ministradas")

    if not df_aulas_mes.empty:
        df_display = df_aulas_mes.copy()
        df_display = df_display.sort_values(by='Data_Dt', ascending=False)

        col_comissao_display = None
        for c in df_display.columns:
            if 'comissão' in c.lower() or 'comissao' in c.lower():
                col_comissao_display = c
                break

        if col_comissao_display:
            df_display[col_comissao_display] = df_display[col_comissao_display].apply(
                lambda v: _fmt_brl(_parse_comissao(v))
            )

        cols_ocultar = ['Data_Dt', 'Mes_Filtro', 'ID Professor', 'Nome Professor']
        cols_exibir = [c for c in df_display.columns if c not in cols_ocultar]

        st.dataframe(
            df_display[cols_exibir],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma aula registrada neste período.")

    st.markdown("")

    # 7. Gestão de Vínculos (Carteira de Alunos)
    st.markdown("##### Carteira de Alunos")

    if df_alunos.empty:
        st.info("Nenhum aluno cadastrado.")
        return

    alunos_ja_vinculados = []
    if not df_links.empty:
        links_prof = df_links[df_links['ID Professor'].astype(str) == id_prof_sel]
        ids_alunos = links_prof['ID Aluno'].astype(str).tolist()
        alunos_ja_vinculados = [mapa_alunos_id_nome[uid] for uid in ids_alunos if uid in mapa_alunos_id_nome]

    with st.container(border=True):
        with st.form("form_update_vinculos"):
            alunos_selecionados = st.multiselect(
                "Alunos vinculados:",
                options=list(mapa_alunos_nome_id.keys()),
                default=alunos_ja_vinculados
            )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Atualizar Carteira de Alunos", use_container_width=True):
                ids_para_salvar = [mapa_alunos_nome_id[nome] for nome in alunos_selecionados]
                try:
                    sucesso, msg = db.salvar_vinculos_do_professor(id_prof_sel, ids_para_salvar)
                    if sucesso:
                        core.notify_success(msg)
                    else:
                        core.notify_error("Erro ao salvar.")
                except Exception as e:
                    core.notify_error(f"Erro: {e}")