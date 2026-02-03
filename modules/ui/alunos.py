import streamlit as st
import database as db
from datetime import date
import re
from modules.ui import core
import pandas as pd

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
    # --- GERENCIAMENTO DE ESTADO ---
    if 'aluno_detalhe_id' not in st.session_state: st.session_state['aluno_detalhe_id'] = None
    def ver_detalhes(id_aluno): st.session_state['aluno_detalhe_id'] = id_aluno
    def voltar_lista(): st.session_state['aluno_detalhe_id'] = None

    # --- CSS ---
    st.markdown("""
        <style>
            div[data-testid="stVerticalBlock"] > div.stButton { text-align: right; }
            .aluno-card-header { font-size: 18px; font-weight: 700; color: #1A1A1A; }
            .aluno-card-sub { font-size: 14px; color: #666; }
            .metric-label { font-size: 12px; color: #888; text-transform: uppercase; font-weight: 600; }
            .metric-value { font-size: 16px; font-weight: 700; color: #1A1A1A; }
            .stProgress > div > div > div > div { background-color: #C5A065; }
        </style>
    """, unsafe_allow_html=True)

    # --- CARREGAMENTO ---
    df_alunos = db.get_alunos()
    
    # Busca dados do Dash
    if hasattr(db, 'get_saldo_alunos'): df_dash = db.get_saldo_alunos()
    else: df_dash = getattr(db, 'get_dash_alunos_data', lambda: pd.DataFrame())()

    # --- MERGE (Usando String para não errar ID) ---
    if not df_alunos.empty and not df_dash.empty:
        # Garante que as chaves sejam strings nos dois lados
        df_alunos['key'] = df_alunos['ID Aluno'].astype(str)
        df_dash['key'] = df_dash['ID Aluno'].astype(str)
        
        # Cruzamento
        df_alunos = df_alunos.merge(
            df_dash[['key', 'Horas Compradas', 'Horas Consumidas', 'Saldo Disponível']], 
            on='key', how='left'
        )

    if df_alunos.empty:
        st.warning("Nenhum aluno encontrado.")
        return

    # --- ORDENAÇÃO INTERNA (Apenas para ordenar a lista, não exibe este valor) ---
    col_saldo = 'Saldo Disponível' if 'Saldo Disponível' in df_alunos.columns else 'Saldo Horas'
    if col_saldo in df_alunos.columns:
        def safe_sort_val(v):
            try: return float(str(v).replace(',', '.'))
            except: return 99999.0
        df_alunos['_ordem'] = df_alunos[col_saldo].apply(safe_sort_val)
        df_alunos = df_alunos.sort_values(by='_ordem', ascending=True)

    # --- MODO 1: LISTA ---
    if st.session_state['aluno_detalhe_id'] is None:
        st.markdown("### 🎓 Gestão de Alunos")
        c_search, _ = st.columns([2, 1])
        busca = c_search.text_input("🔍 Buscar aluno...", placeholder="Digite o nome")
        st.write("")

        df_display = df_alunos.copy()
        if busca:
            df_display = df_display[df_display['Nome Aluno'].astype(str).str.contains(busca, case=False, na=False)]

        for _, row in df_display.iterrows():
            id_aluno = row['ID Aluno']
            nome = row['Nome Aluno']
            serie = row.get('Série', '-')
            
            # --- DADOS PUROS (EXATAMENTE COMO NO EXCEL) ---
            # Se no excel está 4,5 -> Aqui fica "4,5"
            # Se no excel está 4.5 -> Aqui fica 4.5
            raw_total = row.get('Horas Compradas', '-')
            raw_consumido = row.get('Horas Consumidas', '-')
            raw_saldo = row.get('Saldo Disponível', '-')

            # Pequeno ajuste apenas para não mostrar "nan" se estiver vazio
            if pd.isna(raw_total): raw_total = "-"
            if pd.isna(raw_consumido): raw_consumido = "-"
            if pd.isna(raw_saldo) and 'Saldo Horas' in row: raw_saldo = row['Saldo Horas'] # Fallback
            if pd.isna(raw_saldo): raw_saldo = "-"

            # --- BARRA DE PROGRESSO (Cálculo isolado) ---
            progresso = 0.0
            try:
                # Tenta converter APENAS para calcular a % da barra
                # O texto exibido continua sendo o raw_total/raw_consumido
                def to_f(x): return float(str(x).replace(',', '.'))
                ptotal = to_f(raw_total)
                pusado = to_f(raw_consumido)
                if ptotal > 0: progresso = min(pusado / ptotal, 1.0)
            except: 
                progresso = 0.0 # Se der erro no calculo, barra fica zerada, mas texto aparece
            
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    st.markdown(f"<div class='aluno-card-header'>{nome}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='aluno-card-sub'>{serie}</div>", unsafe_allow_html=True)
                with c2:
                    m1, m2, m3 = st.columns(3)
                    # Exibe RAW
                    m1.markdown(f"<div class='metric-label'>Total</div><div class='metric-value'>{raw_total}</div>", unsafe_allow_html=True)
                    m2.markdown(f"<div class='metric-label'>Usadas</div><div class='metric-value'>{raw_consumido}</div>", unsafe_allow_html=True)
                    m3.markdown(f"<div class='metric-label'>Saldo</div><div class='metric-value' style='color:#C5A065'>{raw_saldo}</div>", unsafe_allow_html=True)
                    st.progress(progresso)
                with c3:
                    st.write("")
                    st.button("Ver Detalhes", key=f"btn_{id_aluno}", on_click=ver_detalhes, args=(id_aluno,), use_container_width=True)

    # --- MODO 2: DETALHES ---
    else:
        id_sel = st.session_state['aluno_detalhe_id']
        # Importante: Como convertemos ID para string no inicio, comparamos como string aqui
        row_aluno = df_alunos[df_alunos['ID Aluno'].astype(str) == str(id_sel)]
        
        if not row_aluno.empty:
            data = row_aluno.iloc[0]
            col_voltar, col_tit = st.columns([0.5, 4])
            col_voltar.button("⬅ Voltar", on_click=voltar_lista)
            col_tit.markdown(f"## {data['Nome Aluno']}")
            st.markdown("---")

            c_pes, c_esc = st.columns(2)
            with c_pes:
                with st.container(border=True):
                    st.markdown("**Dados Pessoais**")
                    st.text_input("Responsável", value=str(data.get('Nome Responsável','-')), disabled=True)
                    st.text_input("Telefone", value=str(data.get('Telefone','-')), disabled=True)
                    st.text_input("Nascimento", value=str(data.get('Data Nascimento','-')), disabled=True)
            with c_esc:
                with st.container(border=True):
                    st.markdown("**Dados Escolares**")
                    st.text_input("Série", value=str(data.get('Série','-')), disabled=True)
                    st.text_input("Escola", value=str(data.get('Escola','-')), disabled=True)
                    st.text_input("Endereço", value=str(data.get('Endereço','-')), disabled=True)

            st.write("")
            with st.container(border=True):
                st.markdown("**Equipe de Professores**")
                df_profs = db.get_professores()
                df_links = db.get_vinculos()
                
                map_nome = {r['Nome Professor']: str(r['ID Professor']) for _, r in df_profs.iterrows()}
                map_id = {str(r['ID Professor']): r['Nome Professor'] for _, r in df_profs.iterrows()}
                
                atuais = []
                if not df_links.empty:
                    links = df_links[df_links['ID Aluno'].astype(str) == str(id_sel)]
                    ids = links['ID Professor'].astype(str).tolist()
                    atuais = [map_id[uid] for uid in ids if uid in map_id]
                
                with st.form("form_vinc"):
                    sel = st.multiselect("Professores:", list(map_nome.keys()), default=atuais)
                    c_s, _ = st.columns([1, 4])
                    if c_s.form_submit_button("Salvar Alterações", use_container_width=True):
                        ids_save = [map_nome[n] for n in sel]
                        ok, msg = db.salvar_vinculos_do_aluno(id_sel, ids_save)
                        if ok: core.notify_success(msg)
                        else: core.notify_error(msg)

            st.write("")
            with st.container(border=True):
                st.markdown("**Observações**")
                st.text_area("Notas:", value=str(data.get('Observações','')), height=100, disabled=True)

# (Mantenha o form_novo_aluno