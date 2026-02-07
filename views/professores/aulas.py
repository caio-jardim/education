import streamlit as st
import pandas as pd
import database as db
from datetime import date, time
import time as tm
from modules.ui import core
from modules.ui.core import header_page

def show_page_aulas(id_prof_logado, nome_prof):
    # Cabeçalho original
    header_page("Gestão de Aulas")
    st.write("") 
    
    # --- CSS: PADRÃO VISUAL ---
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
            div[data-testid="stForm"] { border: none !important; box-shadow: none !important; background-color: transparent !important; padding: 0px !important; }
            div[data-testid="stForm"] > div:first-child { padding-top: 0px !important; margin-top: -10px !important; }
            div[data-baseweb="select"] > div { background-color: #FFFFFF !important; border: 1px solid #D1D1D1 !important; color: #1A1A1A !important; }
            div[data-testid="stToastContainer"] { top: 80px; right: 20px; bottom: unset; left: unset; align-items: flex-end; }
        </style>
    """, unsafe_allow_html=True)
    
    tab_lancamento, tab_historico = st.tabs(["📝 Registrar Aula", "📜 Histórico"])
    
    # --- ABA 1: LANÇAR AULA ---
    with tab_lancamento:
        
        # 1. Carrega Dados
        df_alunos_geral = db.get_saldo_alunos()
        df_links = db.get_vinculos()
        df_profs = db.get_professores() 
        
        # 2. Filtragem
        df_alunos_selectbox = pd.DataFrame()
        if not df_links.empty and not df_alunos_geral.empty:
            df_links = df_links.rename(columns={'ID Professor': 'id_prof', 'ID Aluno': 'id_aluno'})
            meus_vinc = df_links[df_links['id_prof'].astype(str) == str(id_prof_logado)]
            ids_permitidos = meus_vinc['id_aluno'].astype(str).tolist()
            col_id = 'ID Aluno' if 'ID Aluno' in df_alunos_geral.columns else 'id_aluno'
            if col_id in df_alunos_geral.columns:
                df_alunos_selectbox = df_alunos_geral[df_alunos_geral[col_id].astype(str).isin(ids_permitidos)]

        # 3. Formulário
        if df_alunos_selectbox.empty:
            st.warning("⚠️ Sem alunos vinculados.")
        else:
            with st.form("form_aula_prof", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    col_nome = 'Nome Aluno' if 'Nome Aluno' in df_alunos_selectbox.columns else 'nome_aluno'
                    lista_alunos = df_alunos_selectbox[col_nome].unique()
                    nome_aluno_selecionado = st.selectbox("Aluno", options=lista_alunos)
                    
                    c_data, c_hora = st.columns(2)
                    data_aula = c_data.date_input("Data", date.today(), format="DD/MM/YYYY")
                    
                    lista_horarios = []
                    for h in range(7, 23):
                        lista_horarios.append(f"{h:02d}:00")
                        if h < 23: lista_horarios.append(f"{h:02d}:30")
                    if "23:00" in lista_horarios: lista_horarios.remove("23:00")
                    if "23:30" in lista_horarios: lista_horarios.remove("23:30")
                    
                    idx_padrao = lista_horarios.index("09:00") if "09:00" in lista_horarios else 0
                    hora_selecionada_str = c_hora.selectbox("Horário", options=lista_horarios, index=idx_padrao)
                
                with col2:
                    duracao = st.number_input("Duração (h)", min_value=0.5, step=0.5, format="%.1f")
                    modalidade = st.selectbox("Modalidade", ["Education", "Online", "Casa"])
                
                obs = st.text_area("Conteúdo / Observações", height=68)
                
                st.markdown("<br>", unsafe_allow_html=True)

                c_btn_save, c_btn_cancel, c_void = st.columns([1.5, 1.5, 6])
                
                with c_btn_save:
                    confirmar = st.form_submit_button("Registrar Aula")
                
                with c_btn_cancel:
                    cancelar = st.form_submit_button("Cancelar", type="secondary")

                if confirmar:
                    try:
                        filtro = df_alunos_geral[df_alunos_geral[col_nome] == nome_aluno_selecionado]
                        if not filtro.empty:
                            col_id_aluno = 'ID Aluno' if 'ID Aluno' in filtro.columns else 'id_aluno'
                            id_aluno_sel = filtro[col_id_aluno].values[0]
                            
                            data_str = data_aula.strftime("%d/%m/%Y")
                            hora_str = hora_selecionada_str 
                            
                            val_hora = 0.0
                            comissao = 0.0
                            if not df_profs.empty:
                                dados_prof = df_profs[df_profs['ID Professor'].astype(str) == str(id_prof_logado)]
                                if not dados_prof.empty:
                                    linha_p = dados_prof.iloc[0]
                                    termo_busca = "Education" if modalidade == "Education" else modalidade.split()[0]
                                    for col in linha_p.keys():
                                        if termo_busca.lower() in col.lower():
                                            v = linha_p[col]
                                            if isinstance(v, (int, float)): val_hora = float(v)
                                            else: 
                                                s = str(v).replace('R$', '').replace('.', '').replace(',', '.').strip()
                                                val_hora = float(s) if s else 0.0
                                            break
                            comissao = val_hora * duracao

                            db.registrar_aula(data_str, hora_str, int(id_aluno_sel), nome_aluno_selecionado, int(id_prof_logado), nome_prof, modalidade, duracao, "Realizada", comissao)
                            core.notify_success(f"Aula registrada!")
                            
                            try:
                                import database.vendas as db_vendas
                                ativou, msg_venda = db_vendas.processar_primeira_aula(id_aluno_sel, data_aula)
                                if ativou: st.toast(f"🎉 {msg_venda}")
                            except: pass
                            
                            st.cache_data.clear()
                            tm.sleep(1)
                            st.rerun()
                        else:
                            st.error("Erro ID.")
                    except Exception as e:
                        st.error(f"Erro: {e}")
                
                if cancelar:
                    st.rerun()

    # --- ABA 2: HISTÓRICO COM FILTRO MENSAL ---
    with tab_historico:
        try:
            df_aulas = db.get_aulas()
            if not df_aulas.empty:
                # 1. Filtra Aulas do Professor Logado
                col_id_prof = next((c for c in df_aulas.columns if 'id' in c.lower() and 'prof' in c.lower()), 'ID Professor')
                minhas_aulas = df_aulas[df_aulas[col_id_prof].astype(str) == str(id_prof_logado)].copy()
                
                if not minhas_aulas.empty:
                    # 2. Tratamento de Data
                    minhas_aulas['Data_Dt'] = pd.to_datetime(minhas_aulas['Data'], format="%d/%m/%Y", errors='coerce')
                    minhas_aulas = minhas_aulas.dropna(subset=['Data_Dt'])
                    minhas_aulas = minhas_aulas.sort_values(by='Data_Dt', ascending=False)
                    
                    # 3. Criação da Coluna Mês/Ano
                    meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
                    minhas_aulas['Mes_Filtro'] = minhas_aulas['Data_Dt'].apply(lambda x: f"{meses_pt[x.month]}/{x.year}")
                    
                    # 4. Selectbox
                    opcoes_meses = minhas_aulas['Mes_Filtro'].unique().tolist()
                    
                    c_filtro, c_vazio = st.columns([2, 4])
                    mes_selecionado = c_filtro.selectbox("Selecione o Mês:", options=opcoes_meses)
                    
                    # 5. Filtragem Final
                    df_exibicao = minhas_aulas[minhas_aulas['Mes_Filtro'] == mes_selecionado]
                    
                    # 6. Limpeza Visual (Remove colunas técnicas)
                    cols_ocultar = ['Data_Dt', 'Mes_Filtro', 'ID Professor', 'id_professor', 'ID Venda', 'ID Vinculo', 'Comissão Professor']
                    cols_finais = [c for c in df_exibicao.columns if c not in cols_ocultar]
                    
                    st.dataframe(df_exibicao[cols_finais], use_container_width=True, hide_index=True)
                    st.caption(f"Total: {len(df_exibicao)} aulas.")
                
                else:
                    st.info("Você ainda não tem aulas registradas.")
            else:
                st.info("Nenhuma aula no sistema.")
        except Exception as e:
            st.error(f"Erro histórico: {e}")