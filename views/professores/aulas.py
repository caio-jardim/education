import streamlit as st
import pandas as pd
import database as db
from datetime import date, time
from modules.ui.core import header_page

def show_page_aulas(id_prof_logado, nome_prof):
    header_page("Gestão de Aulas", "Lançamento e Histórico")
    
    tab_lancamento, tab_historico = st.tabs(["📝 Registrar Nova Aula", "📜 Histórico Completo"])
    
    # --- ABA 1: LANÇAR AULA ---
    with tab_lancamento:
        st.markdown("##### Nova Aula")
        
        # 1. Carrega Dados Necessários
        df_alunos_geral = db.get_saldo_alunos()
        df_links = db.get_vinculos()
        
        # 2. Lógica de Filtragem (RIGOROSA)
        df_alunos_selectbox = pd.DataFrame()
        
        if not df_links.empty and not df_alunos_geral.empty:
            # Padroniza nomes das colunas de vínculo
            df_links = df_links.rename(columns={'ID Professor': 'id_prof', 'ID Aluno': 'id_aluno'})
            
            # Filtra vínculos deste professor
            # Usa astype(str) para garantir que números e textos batam
            meus_vinc = df_links[df_links['id_prof'].astype(str) == str(id_prof_logado)]
            
            # Lista de IDs permitidos
            ids_permitidos = meus_vinc['id_aluno'].astype(str).tolist()
            
            # Filtra a tabela geral de alunos
            # Procura a coluna de ID no dataframe de alunos
            col_id = 'ID Aluno' if 'ID Aluno' in df_alunos_geral.columns else 'id_aluno'
            
            if col_id in df_alunos_geral.columns:
                df_alunos_selectbox = df_alunos_geral[df_alunos_geral[col_id].astype(str).isin(ids_permitidos)]

        # 3. Exibição do Formulário
        if df_alunos_selectbox.empty:
            st.warning("⚠️ Você não possui alunos vinculados para lançar aulas.")
        else:
            with st.form("form_aula_prof", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    col_nome = 'Nome Aluno' if 'Nome Aluno' in df_alunos_selectbox.columns else 'nome_aluno'
                    
                    # Cria lista de nomes apenas dos alunos filtrados
                    lista_alunos = df_alunos_selectbox[col_nome].unique()
                    
                    nome_aluno_selecionado = st.selectbox("Aluno", options=lista_alunos)
                    
                    # DATA E HORÁRIO
                    c_data, c_hora = st.columns(2)
                    data_aula = c_data.date_input("Data", date.today(), format="DD/MM/YYYY")
                    hora_aula = c_hora.time_input("Horário", value=time(8, 0)) 
                
                with col2:
                    duracao = st.number_input("Duração (h)", min_value=0.5, step=0.5, format="%.1f")
                    modalidade = st.selectbox("Modalidade", ["Education", "Online", "Casa"])
                
                obs = st.text_area("Conteúdo / Observações")
                
                if st.form_submit_button("✅ Registrar Aula"):
                    try:
                        # Recupera o ID do aluno selecionado
                        filtro = df_alunos_geral[df_alunos_geral[col_nome] == nome_aluno_selecionado]
                        
                        if not filtro.empty:
                            col_id_aluno = 'ID Aluno' if 'ID Aluno' in filtro.columns else 'id_aluno'
                            id_aluno_sel = filtro[col_id_aluno].values[0]
                            
                            data_str = data_aula.strftime("%d/%m/%Y")
                            hora_str = hora_aula.strftime("%H:%M")
                            
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
                            st.success(f"Aula para {nome_aluno_selecionado} registrada com sucesso!")
                        else:
                            st.error("Erro ao identificar ID do aluno.")
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

    # --- ABA 2: HISTÓRICO ---
    with tab_historico:
        try:
            df_aulas = db.get_aulas()
            if not df_aulas.empty:
                # Normaliza nomes para filtro
                df_aulas = df_aulas.rename(columns={'ID Professor': 'id_prof_aula', 'id_professor': 'id_prof_aula'})
                
                # Filtra aulas deste professor
                if 'id_prof_aula' in df_aulas.columns:
                    minhas_aulas = df_aulas[df_aulas['id_prof_aula'].astype(str) == str(id_prof_logado)]
                    
                    # Exibe tabela (sem índice numérico feio)
                    st.dataframe(minhas_aulas, use_container_width=True, hide_index=True)
                else:
                    st.dataframe(df_aulas)
            else:
                st.info("Nenhuma aula registrada.")
        except Exception as e:
            st.error(f"Erro ao ler histórico: {e}")