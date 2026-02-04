import streamlit as st
import pandas as pd
import database as db
from datetime import date, time # Importa a CLASSE time
import time as tm # Importa a biblioteca para sleep como 'tm'
from modules.ui import core
from modules.ui.core import header_page

def show_page_aulas(id_prof_logado, nome_prof):
    header_page("Gestão de Aulas", "Lançamento e Histórico")
    
    # --- CSS: PADRÃO VISUAL (IGUAL AO ADMIN) ---
    st.markdown("""
        <style>
            /* 1. Formulário Transparente */
            div[data-testid="stForm"] {
                border: none !important;
                box-shadow: none !important;
                background-color: transparent !important;
                padding: 0px !important;
            }
            /* 2. Ajuste Título do Form */
            div[data-testid="stForm"] > div:first-child {
                padding-top: 0px !important;
                margin-top: -10px !important; 
            }
            /* 3. Ajuste do Toast */
            div[data-testid="stToastContainer"] {
                top: 80px; right: 20px; bottom: unset; left: unset; align-items: flex-end;
            }
        </style>
    """, unsafe_allow_html=True)
    
    tab_lancamento, tab_historico = st.tabs(["📝 Registrar Nova Aula", "📜 Histórico Completo"])
    
    # --- ABA 1: LANÇAR AULA ---
    with tab_lancamento:
        
        # 1. Carrega Dados
        df_alunos_geral = db.get_saldo_alunos()
        df_links = db.get_vinculos()
        
        # 2. Lógica de Filtragem (Aluno vinculado ao Prof)
        df_alunos_selectbox = pd.DataFrame()
        
        if not df_links.empty and not df_alunos_geral.empty:
            df_links = df_links.rename(columns={'ID Professor': 'id_prof', 'ID Aluno': 'id_aluno'})
            meus_vinc = df_links[df_links['id_prof'].astype(str) == str(id_prof_logado)]
            ids_permitidos = meus_vinc['id_aluno'].astype(str).tolist()
            
            col_id = 'ID Aluno' if 'ID Aluno' in df_alunos_geral.columns else 'id_aluno'
            
            if col_id in df_alunos_geral.columns:
                df_alunos_selectbox = df_alunos_geral[df_alunos_geral[col_id].astype(str).isin(ids_permitidos)]

        # 3. Exibição do Formulário
        if df_alunos_selectbox.empty:
            st.warning("⚠️ Você não possui alunos vinculados para lançar aulas. Entre em contato com a administração.")
        else:
            with st.form("form_aula_prof", clear_on_submit=True):
                
                # CABEÇALHO DO FORM (PADRÃO NOVO)
                c_icon, c_title = st.columns([0.5, 10])
                with c_icon: st.markdown("📝")
                with c_title: st.markdown("### Nova Aula")

                # LINHA 1: ALUNO
                col_nome = 'Nome Aluno' if 'Nome Aluno' in df_alunos_selectbox.columns else 'nome_aluno'
                lista_alunos = df_alunos_selectbox[col_nome].unique()
                nome_aluno_selecionado = st.selectbox("Aluno", options=lista_alunos)
                
                # LINHA 2: DATA E HORÁRIO (CORREÇÃO AQUI)
                c_data, c_hora = st.columns(2)
                data_aula = c_data.date_input("Data", date.today(), format="DD/MM/YYYY")
                
                # --- SOLUÇÃO SELECTBOX (IGUAL ADMIN) ---
                lista_horarios = []
                for h in range(7, 23):
                    lista_horarios.append(f"{h:02d}:00")
                    if h < 23: lista_horarios.append(f"{h:02d}:30")
                
                if "23:00" in lista_horarios: lista_horarios.remove("23:00")
                if "23:30" in lista_horarios: lista_horarios.remove("23:30")
                
                idx_padrao = lista_horarios.index("09:00") if "09:00" in lista_horarios else 0
                
                # O Selectbox substitui o time_input problemático
                hora_selecionada_str = c_hora.selectbox("Horário", options=lista_horarios, index=idx_padrao)
                
                # LINHA 3: DURAÇÃO E MODALIDADE
                c_dur, c_mod = st.columns(2)
                duracao = c_dur.number_input("Duração (h)", min_value=0.5, step=0.5, format="%.1f")
                modalidade = c_mod.selectbox("Modalidade", ["Education", "Online", "Casa"])
                
                obs = st.text_area("Conteúdo / Observações")
                
                st.markdown("<br>", unsafe_allow_html=True)

                # --- BOTÕES PADRONIZADOS ---
                c_btn_save, c_btn_cancel, c_void = st.columns([1.5, 1.5, 6])
                
                with c_btn_save:
                    confirmar = st.form_submit_button("✅ Registrar")
                
                with c_btn_cancel:
                    cancelar = st.form_submit_button("❌ Cancelar", type="secondary")

                # --- LÓGICA DE AÇÃO ---
                if confirmar:
                    try:
                        filtro = df_alunos_geral[df_alunos_geral[col_nome] == nome_aluno_selecionado]
                        
                        if not filtro.empty:
                            col_id_aluno = 'ID Aluno' if 'ID Aluno' in filtro.columns else 'id_aluno'
                            id_aluno_sel = filtro[col_id_aluno].values[0]
                            
                            data_str = data_aula.strftime("%d/%m/%Y")
                            hora_str = hora_selecionada_str # Já vem pronta do selectbox
                            
                            # 1. Registra a Aula
                            db.registrar_aula(
                                data_str, 
                                hora_str, 
                                int(id_aluno_sel), 
                                nome_aluno_selecionado, 
                                int(id_prof_logado), 
                                nome_prof, 
                                modalidade, 
                                duracao, 
                                "Realizada"
                            )
                            core.notify_success(f"Aula registrada com sucesso!")
                            
                            # 2. Ativação de Pacote (Lógica de Negócio)
                            try:
                                import database.vendas as db_vendas
                                ativou, msg_venda = db_vendas.processar_primeira_aula(id_aluno_sel, data_aula)
                                if ativou:
                                    st.toast(f"🎉 {msg_venda}")
                            except: pass
                            
                            st.cache_data.clear()
                            tm.sleep(1)
                            st.rerun()
                            
                        else:
                            st.error("Erro ao identificar ID do aluno.")
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")
                
                if cancelar:
                    st.rerun()

    # --- ABA 2: HISTÓRICO ---
    with tab_historico:
        try:
            df_aulas = db.get_aulas()
            if not df_aulas.empty:
                df_aulas = df_aulas.rename(columns={'ID Professor': 'id_prof_aula', 'id_professor': 'id_prof_aula'})
                if 'id_prof_aula' in df_aulas.columns:
                    minhas_aulas = df_aulas[df_aulas['id_prof_aula'].astype(str) == str(id_prof_logado)]
                    st.dataframe(minhas_aulas, use_container_width=True, hide_index=True)
                else:
                    st.dataframe(df_aulas)
            else:
                st.info("Nenhuma aula registrada ainda.")
        except Exception as e:
            st.error(f"Erro ao ler histórico: {e}")