import streamlit as st
import database as db
from datetime import datetime, date
import re
from modules.ui import core
import pandas as pd

def form_novo_aluno():
    # --- CSS ESPECÍFICO DESTA TELA ---
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
        with c_icon: st.image("assets/icon_novo_aluno.png", width=45) 
        with c_title: st.markdown("### Novo Aluno")

        # Campos Pessoais
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

        # --- SEÇÃO PACOTE (CONDICIONAL) ---
        c_icon2, c_title2 = st.columns([0.5, 10])
        with c_icon2: st.image("assets/icon_novo_pacote.png", width=45)
        with c_title2: st.markdown("### Primeiro Pacote")
        
        # Checkbox para ativar/desativar pacote inicial
        gerar_pacote = st.checkbox("Incluir Pacote Inicial / Matrícula?", value=True, help="Desmarque se for aluno avulso ou sem pacote definido agora.")
        
        # Inicializa variáveis para não quebrar o código
        qtd_horas = 0
        data_contrato = date.today()
        pagou_agora = False
        data_pagamento = None
        
        if gerar_pacote:
            c1, c2, c3 = st.columns(3)
            qtd_horas = c1.number_input("Qtd Horas", min_value=1.0, step=0.5, format="%.1f")
            data_contrato = c2.date_input("Data Contratação", format="DD/MM/YYYY")
            pagou_agora = c3.checkbox("Já pagou?", value=True)
            data_pagamento = st.date_input("Data Pagamento", value=date.today(), format="DD/MM/YYYY") if pagou_agora else None
        else:
            st.caption("ℹ️ O aluno será criado apenas com saldo zerado. Você poderá lançar pacotes depois na aba 'Vendas'.")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- BOTÕES DE AÇÃO ---
        c_btn_save, c_btn_cancel, c_void = st.columns([1.5, 1.5, 6])
        
        with c_btn_save:
            submit = st.form_submit_button("Salvar Cadastro")
        
        with c_btn_cancel:
            cancel = st.form_submit_button("Cancelar", type="secondary")

        if cancel: st.rerun()

        if submit:
            if not nome: 
                core.notify_warning("Nome obrigatório")
            else:
                try:
                    # Formatações básicas
                    nasc_str = nascimento.strftime("%d/%m/%Y") if nascimento else ""
                    
                    # 1. Salvar Aluno (SEMPRE)
                    novo_id = db.cadastrar_aluno(nome, responsavel, telefone, nasc_str, serie, escola, endereco, obs)
                    
                    # 2. Salvar Vínculos (SEMPRE)
                    ids_vincular = [mapa_professores[p] for p in profs_selecionados]
                    if ids_vincular:
                        db.salvar_vinculos_do_aluno(novo_id, ids_vincular)
                    
                    # 3. Salvar Venda (CONDICIONAL)
                    if gerar_pacote:
                        contrato_str = data_contrato.strftime("%d/%m/%Y")
                        pagamento_str = data_pagamento.strftime("%d/%m/%Y") if data_pagamento else ""
                        
                        sucesso, msg = db.registrar_venda_automatica(novo_id, nome, qtd_horas, "Pix", contrato_str, pagamento_str)
                        
                        if sucesso:
                            core.notify_success(f"Aluno {nome} criado e pacote lançado!")
                        else:
                            core.notify_warning(f"Aluno criado, mas erro na venda: {msg}")
                    else:
                        # Se não teve pacote, avisa apenas que o aluno foi criado
                        core.notify_success(f"Aluno {nome} cadastrado com sucesso (sem pacote inicial).")

                    # Reset e Refresh
                    st.session_state['reset_counter_aluno'] += 1
                    import time
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
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
            .aluno-card-header { font-size: 16px; font-weight: 700; color: #1A1A1A; }
            .aluno-card-sub { font-size: 13px; color: #666; }
            .metric-label { font-size: 11px; color: #888; text-transform: uppercase; font-weight: 600; }
            .metric-value { font-size: 15px; font-weight: 700; color: #1A1A1A; }
            .stProgress > div > div > div > div { background-color: #C5A065; }
            .col-header { font-size: 16px; font-weight: 600; color: #555; margin-bottom: 10px; border-bottom: 2px solid #eee; padding-bottom: 5px; }
            
            /* Tags de Vencimento */
            .tag-vencido { color: #D32F2F; font-weight: 700; font-size: 12px; background: #FFEBEE; padding: 2px 6px; border-radius: 4px; }
            .tag-atencao { color: #F57C00; font-weight: 700; font-size: 12px; background: #FFF3E0; padding: 2px 6px; border-radius: 4px; }
            .tag-ok { color: #388E3C; font-weight: 700; font-size: 12px; background: #E8F5E9; padding: 2px 6px; border-radius: 4px; }
            
            div[data-testid="stForm"] {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 1.5rem;
                background-color: #FFFFFF;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- 1. CARREGAMENTO DE DADOS ---
    df_alunos = db.get_alunos()
    
    # Saldo de Horas
    if hasattr(db, 'get_saldo_alunos'): df_dash = db.get_saldo_alunos()
    else: df_dash = getattr(db, 'get_dash_alunos_data', lambda: pd.DataFrame())()

    # Vencimentos (Lógica Nova)
    df_vencimentos = pd.DataFrame()
    try:
        # Tenta pegar as vendas para achar os vencimentos
        if hasattr(db, 'get_vendas'):
            df_raw_vendas = db.get_vendas()
        else:
            # Fallback: tenta pegar do financeiro se tiver as colunas
            df_raw_vendas = db.get_financeiro_geral()
            
        if not df_raw_vendas.empty and 'Data Vencimento Pacote' in df_raw_vendas.columns:
            # Converte data
            df_raw_vendas['dt_venc'] = pd.to_datetime(df_raw_vendas['Data Vencimento Pacote'], format='%d/%m/%Y', errors='coerce')
            
            # Pega a MAIOR data de vencimento por aluno (o pacote mais recente)
            # Renomeia se necessário para garantir ID Aluno
            col_id_venda = 'ID Aluno' if 'ID Aluno' in df_raw_vendas.columns else 'id_aluno'
            
            if col_id_venda in df_raw_vendas.columns:
                df_vencimentos = df_raw_vendas.groupby(col_id_venda)['dt_venc'].max().reset_index()
                df_vencimentos.columns = ['key', 'max_vencimento']
                df_vencimentos['key'] = df_vencimentos['key'].astype(str)
    except Exception as e:
        print(f"Erro ao calcular vencimentos: {e}")

    # --- 2. MERGE DE TUDO ---
    if not df_alunos.empty:
        df_alunos['key'] = df_alunos['ID Aluno'].astype(str)
        if not df_dash.empty:
            df_dash['key'] = df_dash['ID Aluno'].astype(str)
            df_alunos = df_alunos.merge(df_dash[['key', 'Horas Compradas', 'Horas Consumidas', 'Saldo Disponível']], on='key', how='left')
        
        if not df_vencimentos.empty:
            df_alunos = df_alunos.merge(df_vencimentos, on='key', how='left')

    if df_alunos.empty:
        st.warning("Nenhum aluno encontrado.")
        return

    # --- 3. CÁLCULOS DE ORDENAÇÃO ---
    # Saldo Numérico
    col_saldo = 'Saldo Disponível' if 'Saldo Disponível' in df_alunos.columns else 'Saldo Horas'
    def safe_float(v):
        try: return float(str(v).replace(',', '.'))
        except: return 0.0
    
    df_alunos['_saldo_num'] = df_alunos[col_saldo].apply(safe_float)

    # Dias Restantes
    hoje = pd.to_datetime(date.today())
    def calc_dias(row):
        if 'max_vencimento' in row and not pd.isnull(row['max_vencimento']):
            delta = (row['max_vencimento'] - hoje).days
            return delta
        return 9999 # Se não tem data, joga pro final da fila de prioridade
    
    df_alunos['_dias_restantes'] = df_alunos.apply(calc_dias, axis=1)

    # --- LÓGICA DE ORDENAÇÃO PEDIDA ---
    # 1º Prioridade: Dias Restantes (Menor para Maior) -> Quem vence logo ou já venceu aparece antes
    # 2º Prioridade: Saldo de Horas (Menor para Maior) -> Quem tem menos horas aparece antes
    df_alunos = df_alunos.sort_values(by=['_dias_restantes', '_saldo_num'], ascending=[True, True])

    # --- MODO 1: LISTA (VISÃO GERAL) ---
    if st.session_state['aluno_detalhe_id'] is None:
        st.markdown("### 🎓 Gestão de Alunos")
        
        c_search, _ = st.columns([2, 1])
        busca = c_search.text_input("🔍 Buscar aluno...", placeholder="Digite o nome")
        st.write("")

        df_display = df_alunos.copy()
        if busca:
            df_display = df_display[df_display['Nome Aluno'].astype(str).str.contains(busca, case=False, na=False)]

        # Separação
        df_ativos = df_display[df_display['_saldo_num'] > 0.01]
        df_zerados = df_display[df_display['_saldo_num'] <= 0.01]

        col_ativos, col_zerados = st.columns(2)

        def render_card_aluno(row):
            id_aluno = row['ID Aluno']
            nome = row['Nome Aluno']
            serie = row.get('Série', '-')
            
            raw_total = row.get('Horas Compradas', '-')
            raw_consumido = row.get('Horas Consumidas', '-')
            raw_saldo = row.get('Saldo Disponível', '-')
            dias = row['_dias_restantes']

            # Tratamento visual de NaN
            if pd.isna(raw_total): raw_total = "-"
            if pd.isna(raw_consumido): raw_consumido = "-"
            if pd.isna(raw_saldo): raw_saldo = "-"

            # Barra de progresso
            progresso = 0.0
            try:
                ptotal = safe_float(raw_total)
                pusado = safe_float(raw_consumido)
                if ptotal > 0: progresso = min(pusado / ptotal, 1.0)
            except: pass
            
            with st.container(border=True):
                l1, l2 = st.columns([3, 1])
                with l1:
                    st.markdown(f"<div class='aluno-card-header'>{nome}</div>", unsafe_allow_html=True)
                    
                    # --- NOVA INFO: DIAS RESTANTES ---
                    tag_html = ""
                    if dias != 9999:
                        if dias < 0:
                            tag_html = f"<span class='tag-vencido'>Vencido há {abs(dias)} dias</span>"
                        elif dias <= 5:
                            tag_html = f"<span class='tag-vencido'>Vence em {dias} dias</span>"
                        elif dias <= 10:
                            tag_html = f"<span class='tag-atencao'>Vence em {dias} dias</span>"
                        else:
                            tag_html = f"<span class='tag-ok'>{dias} dias restantes</span>"
                    else:
                        tag_html = "<span style='font-size:11px; color:#999'>Sem vencimento</span>"
                        
                    st.markdown(f"<div style='margin-top:2px; margin-bottom:4px;'>{tag_html} <span class='aluno-card-sub'> • {serie}</span></div>", unsafe_allow_html=True)

                with l2:
                    if st.button("Ver", key=f"btn_{id_aluno}"):
                        ver_detalhes(id_aluno)
                        st.rerun()

                st.markdown("---")
                
                m1, m2, m3 = st.columns(3)
                m1.markdown(f"<div class='metric-label'>Total</div><div class='metric-value'>{raw_total}</div>", unsafe_allow_html=True)
                m2.markdown(f"<div class='metric-label'>Usadas</div><div class='metric-value'>{raw_consumido}</div>", unsafe_allow_html=True)
                
                # Cor condicional no saldo (Vermelho se < 1h)
                cor_saldo = "#C5A065"
                if row['_saldo_num'] <= 1: cor_saldo = "#E53935"
                
                m3.markdown(f"<div class='metric-label'>Saldo</div><div class='metric-value' style='color:{cor_saldo}'>{raw_saldo}</div>", unsafe_allow_html=True)
                
                st.progress(progresso)

        with col_ativos:
            st.markdown("<div class='col-header'>Ativos</div>", unsafe_allow_html=True)
            if df_ativos.empty: st.info("Nenhum aluno ativo.")
            else:
                for _, row in df_ativos.iterrows(): render_card_aluno(row)

        with col_zerados:
            st.markdown("<div class='col-header'>Finalizados</div>", unsafe_allow_html=True)
            if df_zerados.empty: st.caption("Nenhum aluno zerado.")
            else:
                for _, row in df_zerados.iterrows(): render_card_aluno(row)

    # --- MODO 2: DETALHES (EDIÇÃO) - MANTIDO IGUAL ---
    else:
        id_sel = st.session_state['aluno_detalhe_id']
        row_aluno = df_alunos[df_alunos['ID Aluno'].astype(str) == str(id_sel)]
        
        if not row_aluno.empty:
            data = row_aluno.iloc[0]
            col_voltar, col_tit = st.columns([0.5, 4])
            col_voltar.button("⬅ Voltar", on_click=voltar_lista)
            col_tit.markdown(f"## {data['Nome Aluno']}")
            st.markdown("---")

            # --- FORMULÁRIO DE EDIÇÃO ---
            with st.form("form_editar_aluno", clear_on_submit=False):
                st.markdown("##### 📝 Dados Cadastrais")
                
                c_pes, c_esc = st.columns(2)
                
                with c_pes:
                    st.caption("Dados Pessoais")
                    val_nome = str(data.get('Nome Aluno', ''))
                    val_resp = str(data.get('Nome Responsável', '')) if not pd.isna(data.get('Nome Responsável')) else ""
                    val_tel = str(data.get('Telefone', '')) if not pd.isna(data.get('Telefone')) else ""
                    val_nasc_str = str(data.get('Data Nascimento', '')) if not pd.isna(data.get('Data Nascimento')) else ""
                    
                    val_nasc_date = None
                    try: val_nasc_date = datetime.strptime(val_nasc_str, "%d/%m/%Y").date()
                    except: val_nasc_date = None

                    novo_nome = st.text_input("Nome do Aluno", value=val_nome)
                    novo_resp = st.text_input("Responsável", value=val_resp)
                    novo_tel = st.text_input("Telefone", value=val_tel)
                    
                    novo_nasc = st.date_input("Nascimento", value=val_nasc_date, format="DD/MM/YYYY") if val_nasc_date else st.date_input("Nascimento", value=None, format="DD/MM/YYYY")

                with c_esc:
                    st.caption("Dados Escolares")
                    val_serie = str(data.get('Série', '')) if not pd.isna(data.get('Série')) else ""
                    val_escola = str(data.get('Escola', '')) if not pd.isna(data.get('Escola')) else ""
                    val_end = str(data.get('Endereço', '')) if not pd.isna(data.get('Endereço')) else ""

                    novo_serie = st.text_input("Série", value=val_serie)
                    novo_escola = st.text_input("Escola", value=val_escola)
                    novo_end = st.text_input("Endereço", value=val_end)

                st.markdown("<br>", unsafe_allow_html=True)
                val_obs = str(data.get('Observações', '')) if not pd.isna(data.get('Observações')) else ""
                novo_obs = st.text_area("Observações", value=val_obs, height=80)

                st.markdown("<br>", unsafe_allow_html=True)
                
                # Botões Padronizados
                c_save, c_cancel, c_void = st.columns([1.5, 1.5, 6])
                
                with c_save:
                    salvar = st.form_submit_button("Salvar")
                with c_cancel:
                    cancelar_edicao = st.form_submit_button("Cancelar", type="secondary")

                if salvar:
                    try:
                        nasc_final_str = novo_nasc.strftime("%d/%m/%Y") if novo_nasc else ""
                        if hasattr(db, 'atualizar_aluno'):
                            db.atualizar_aluno(id_sel, novo_nome, novo_resp, novo_tel, nasc_final_str, novo_serie, novo_escola, novo_end, novo_obs)
                            st.success("Cadastro atualizado!")
                            st.cache_data.clear()
                            import time
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Função 'db.atualizar_aluno' não encontrada.")
                    except Exception as e:
                        st.error(f"Erro ao atualizar: {e}")
                
                if cancelar_edicao:
                    st.rerun()

            st.write("")
            with st.container(border=True):
                st.markdown("##### 👥 Equipe de Professores")
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
                    sel = st.multiselect("Professores Vinculados:", list(map_nome.keys()), default=atuais)
                    c_s, _ = st.columns([1.5, 4])
                    if c_s.form_submit_button("Atualizar Equipe"):
                        ids_save = [map_nome[n] for n in sel]
                        ok, msg = db.salvar_vinculos_do_aluno(id_sel, ids_save)
                        if ok: st.success(msg)
                        else: st.error(msg)

