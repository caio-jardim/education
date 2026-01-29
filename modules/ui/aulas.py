import streamlit as st
import database as db
from datetime import date, datetime
import pandas as pd

def show_gestao_aulas():
    st.markdown("### 📅 Gestão de Aulas")
    
    tab_agenda, tab_novo, tab_lista = st.tabs(["🗓️ Agenda & Ações", "➕ Novo Registro", "📜 Histórico Completo"])
    
    df_aulas = db.get_aulas()
    
    # --- TAB 1: AGENDA (Aulas Agendadas) ---
    with tab_agenda:
        st.markdown("#### Aulas Agendadas")
        if not df_aulas.empty and 'Status' in df_aulas.columns:
            # Filtra só o que está agendado
            df_agendadas = df_aulas[df_aulas['Status'] == 'Agendada'].copy()
            
            if not df_agendadas.empty:
                # Converte data para ordenar
                df_agendadas['Data_Dt'] = pd.to_datetime(df_agendadas['Data'], format="%d/%m/%Y", errors='coerce')
                df_agendadas = df_agendadas.sort_values('Data_Dt')
                
                for index, row in df_agendadas.iterrows():
                    with st.container(border=True):
                        c1, c2, c3, c4, c5 = st.columns([2, 3, 3, 2, 3])
                        
                        c1.markdown(f"**{row['Data']}**")
                        c2.markdown(f"👤 {row['Nome Aluno']}")
                        c3.markdown(f"👨‍🏫 {row['Nome Professor']}")
                        c4.caption(f"{row['Modalidade']}")
                        
                        # Botões de Ação
                        with c5:
                            # Usamos keys únicas para cada botão não conflitar
                            col_btn1, col_btn2 = st.columns(2)
                            if col_btn1.button("✅", key=f"ok_{row['ID Aula']}", help="Marcar como Realizada"):
                                db.atualizar_status_aula(row['ID Aula'], "Realizada")
                                st.success("Aula realizada!")
                                st.rerun()
                                
                            if col_btn2.button("❌", key=f"cancel_{row['ID Aula']}", help="Cancelar Aula"):
                                db.atualizar_status_aula(row['ID Aula'], "Cancelada c/ custo") # Padrão
                                st.warning("Aula cancelada.")
                                st.rerun()
            else:
                st.info("Nenhuma aula pendente de realização.")
        else:
            st.info("Nenhuma aula encontrada.")

    # --- TAB 2: NOVO REGISTRO (Agendar ou Registrar Passada) ---
    with tab_novo:
        st.markdown("##### Cadastro de Aula")
        
        # Carrega dados
        df_alunos = db.get_alunos()
        df_profs = db.get_professores()
        
        mapa_alunos = dict(zip(df_alunos['Nome Aluno'], df_alunos['ID Aluno'])) if not df_alunos.empty else {}
        mapa_profs = dict(zip(df_profs['Nome Professor'], df_profs['ID Professor'])) if not df_profs.empty else {}
        
        with st.form("form_aula_nova", clear_on_submit=True):
            col_tipo = st.radio("O que deseja fazer?", ["Agendar Futura", "Registrar Aula que já aconteceu"], horizontal=True)
            
            c1, c2 = st.columns(2)
            with c1:
                nome_aluno = st.selectbox("Aluno", list(mapa_alunos.keys()))
                nome_prof = st.selectbox("Professor", list(mapa_profs.keys()))
                data_aula = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
            
            with c2:
                modalidade = st.selectbox("Modalidade", ["Online", "Education", "Casa"])
                duracao = st.number_input("Duração (Horas)", min_value=0.5, step=0.5, value=1.0)
                
            # Define o status inicial baseado na escolha do rádio
            status_inicial = "Agendada" if col_tipo == "Agendar Futura" else "Realizada"
            
            submit = st.form_submit_button(f"💾 Salvar como '{status_inicial}'")
            
            if submit:
                if not nome_aluno or not nome_prof:
                    st.error("Preencha Aluno e Professor.")
                else:
                    data_str = data_aula.strftime("%d/%m/%Y")
                    id_aluno = mapa_alunos[nome_aluno]
                    id_prof = mapa_profs[nome_prof]
                    
                    try:
                        # O cálculo da comissão é feito automático lá no db.registrar_aula
                        db.registrar_aula(data_str, id_aluno, nome_aluno, id_prof, nome_prof, modalidade, duracao, status_inicial)
                        st.success(f"Aula salva com status: {status_inicial}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

    # --- TAB 3: HISTÓRICO COMPLETO ---
    with tab_lista:
        st.markdown("##### Histórico Geral")
        if not df_aulas.empty:
            # Filtros simples
            filtro_status = st.multiselect("Filtrar Status", df_aulas['Status'].unique(), default=df_aulas['Status'].unique())
            
            df_show = df_aulas[df_aulas['Status'].isin(filtro_status)]
            
            # Mostra colunas limpas
            cols = ['Data', 'Nome Aluno', 'Nome Professor', 'Modalidade', 'Duração', 'Status', 'Comissão Professor']
            validas = [c for c in cols if c in df_show.columns]
            
            st.dataframe(df_show[validas], use_container_width=True, hide_index=True)