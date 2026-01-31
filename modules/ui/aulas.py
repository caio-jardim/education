import streamlit as st
import database as db
from modules.ui import core
from datetime import date, datetime, timedelta, time
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
import pandas as pd

def show_gestao_aulas():
    # CSS Toast
    st.markdown("""<style>div[data-testid="stToastContainer"] {top: 80px; right: 20px; bottom: unset; left: unset; align-items: flex-end;}</style>""", unsafe_allow_html=True)

    st.markdown("### 📅 Gestão de Aulas")
    
    tab_agenda, tab_novo, tab_lista = st.tabs(["🗓️ Agenda Dinâmica", "➕ Novo Lançamento", "📜 Histórico"])
    
    df_aulas = db.get_aulas()
    
    # --- TAB 1: AGENDA (VISUALIZAÇÃO) ---
    with tab_agenda:
        if not df_aulas.empty and 'Status' in df_aulas.columns:
            # Filtra Apenas Agendadas
            df_agendadas = df_aulas[df_aulas['Status'] == 'Agendada'].copy()
            
            if not df_agendadas.empty:
                # Tratamento de Data/Hora para ordenação
                df_agendadas['Data_Dt'] = pd.to_datetime(df_agendadas['Data'], format="%d/%m/%Y", errors='coerce')
                col_ordem = ['Data_Dt']
                if 'Horário' in df_agendadas.columns:
                    col_ordem.append('Horário')
                
                df_agendadas = df_agendadas.sort_values(by=col_ordem)
                
                dias_unicos = df_agendadas['Data_Dt'].dropna().unique()
                
                for dia in dias_unicos:
                    dia_str = pd.to_datetime(dia).strftime("%d/%m/%Y")
                    dia_semana = pd.to_datetime(dia).strftime("%A")
                    mapa_semana = {'Monday':'Segunda', 'Tuesday':'Terça', 'Wednesday':'Quarta', 'Thursday':'Quinta', 'Friday':'Sexta', 'Saturday':'Sábado', 'Sunday':'Domingo'}
                    dia_pt = mapa_semana.get(dia_semana, dia_semana)
                    
                    st.markdown(f"##### 📆 {dia_str} <span style='color:gray; font-size:0.8em'>({dia_pt})</span>", unsafe_allow_html=True)
                    
                    aulas_dia = df_agendadas[df_agendadas['Data_Dt'] == dia]
                    
                    for _, row in aulas_dia.iterrows():
                        with st.container(border=True):
                            c1, c2, c3, c4 = st.columns([1.5, 4, 2, 2])
                            horario = row.get('Horário', '00:00')
                            c1.markdown(f"**⏰ {horario}**")
                            c2.markdown(f"**{row['Nome Aluno']}**")
                            c2.caption(f"Prof. {row['Nome Professor']}")
                            c3.caption(f"{row['Modalidade']} • {row['Duração']}h")
                            
                            with c4:
                                ca, cb = st.columns(2)
                                if ca.button("✅", key=f"ok_{row['ID Aula']}", help="Confirmar Realização"):
                                    db.atualizar_status_aula(row['ID Aula'], "Realizada")
                                    st.rerun()
                                if cb.button("❌", key=f"cancel_{row['ID Aula']}", help="Cancelar"):
                                    db.atualizar_status_aula(row['ID Aula'], "Cancelada c/ Custo")
                                    st.rerun()
            else:
                st.info("Nenhuma aula futura na agenda.")
        else:
            st.info("Sem dados de aulas.")

    # --- TAB 2: NOVO LANÇAMENTO (COM OPÇÃO DE STATUS) ---
    with tab_novo:
        st.markdown("##### 📝 Dados da Aula")
        
        # Carregamentos
        df_alunos = db.get_alunos()
        df_profs = db.get_professores()
        mapa_alunos = dict(zip(df_alunos['Nome Aluno'], df_alunos['ID Aluno'])) if not df_alunos.empty else {}
        mapa_profs = dict(zip(df_profs['Nome Professor'], df_profs['ID Professor'])) if not df_profs.empty else {}
        
        with st.form("form_aula_inteligente"):
            # --- AQUI ESTÁ A OPÇÃO QUE VOCÊ PEDIU ---
            tipo_registro = st.radio(
                "O que deseja fazer?", 
                ["Agendar Aula Futura", "Registrar Aula Realizada"], 
                horizontal=True
            )
            # Define o status automático com base na escolha
            status_automatico = "Agendada" if tipo_registro == "Agendar Aula Futura" else "Realizada"
            
            st.markdown("---")
            
            # Linha 1: Quem
            c1, c2, c3 = st.columns(3)
            aluno = c1.selectbox("Aluno", list(mapa_alunos.keys()))
            prof = c2.selectbox("Professor", list(mapa_profs.keys()))
            modalidade = c3.selectbox("Modalidade", ["Online", "Education", "Casa"])
            
            # Linha 2: Quando
            c4, c5, c6 = st.columns(3)
            data_inicio = c4.date_input("Data", value=date.today(), format="DD/MM/YYYY")
            hora_inicio = c5.time_input("Horário", value=time(9, 0))
            duracao = c6.number_input("Duração (h)", value=1.0, step=0.5)
            
            # Linha 3: Recorrência
            st.markdown("###### 🔁 Repetição")
            col_rep, col_qtd = st.columns([2, 1])
            tipo_rep = col_rep.selectbox("Frequência", ["Uma única vez", "Diariamente", "Semanalmente", "Mensalmente"], index=0)
            
            qtd_repeticoes = 1
            if tipo_rep != "Uma única vez":
                qtd_repeticoes = col_qtd.number_input("Repetir por quantas vezes?", min_value=2, value=4, step=1)

            # Geração das Datas
            datas_geradas = [data_inicio]
            if tipo_rep != "Uma única vez":
                freq_map = {"Diariamente": DAILY, "Semanalmente": WEEKLY, "Mensalmente": MONTHLY}
                datas_geradas = list(rrule(
                    freq=freq_map[tipo_rep],
                    dtstart=datetime.combine(data_inicio, hora_inicio),
                    count=qtd_repeticoes
                ))
                datas_geradas = [d.date() for d in datas_geradas]

            # Preview Discreto
            if len(datas_geradas) > 1:
                st.caption(f"ℹ️ Serão criados **{len(datas_geradas)} registros** com status **'{status_automatico}'**.")

            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button(f"💾 Salvar {len(datas_geradas)} Aula(s)", use_container_width=True)
            
            if submit:
                if not aluno or not prof:
                    core.notify_warning("Selecione Aluno e Professor.")
                else:
                    try:
                        id_a = mapa_alunos[aluno]
                        id_p = mapa_profs[prof]
                        hora_str = hora_inicio.strftime("%H:%M")
                        
                        # Cálculo Rápido de Comissão (Recuperando valor hora do prof)
                        val_hora = 0.0
                        # Filtra o DF de professores carregado lá em cima
                        dados_prof = df_profs[df_profs['ID Professor'].astype(str) == str(id_p)]
                        
                        if not dados_prof.empty:
                            linha_p = dados_prof.iloc[0]
                            # Tenta achar a coluna certa (Online, Casa, etc)
                            termo_busca = modalidade.split()[0] # Pega 'Online' de 'Online' ou 'Education'
                            if modalidade == "Education": termo_busca = "Education"
                            
                            for col in linha_p.keys():
                                if termo_busca.lower() in col.lower():
                                    val_raw = linha_p[col]
                                    # Limpa valor (R$ 50,00 -> 50.0)
                                    if isinstance(val_raw, (int, float)): val_hora = float(val_raw)
                                    else:
                                        s = str(val_raw).replace('R$', '').replace('.', '').replace(',', '.').strip()
                                        val_hora = float(s) if s else 0.0
                                    break
                        
                        comissao = val_hora * duracao
                        lote_para_salvar = []

                        # Loop para criar as linhas
                        for d in datas_geradas:
                            # [Data, Hora, ID A, Nome A, ID P, Nome P, Modalidade, Duração, Status, Comissão]
                            lote_para_salvar.append([
                                d.strftime("%d/%m/%Y"),
                                hora_str,
                                id_a,
                                aluno,
                                id_p,
                                prof,
                                modalidade,
                                str(duracao).replace('.', ','),
                                status_automatico, # Aqui entra o status escolhido no Radio Button
                                comissao
                            ])
                        
                        sucesso, msg = db.registrar_lote_aulas(lote_para_salvar)
                        
                        if sucesso:
                            core.notify_success(msg)
                            st.rerun()
                            
                    except Exception as e:
                        core.notify_error(f"Erro técnico: {e}")

    # --- TAB 3: HISTÓRICO ---
    with tab_lista:
        st.markdown("##### Histórico Geral")
        if not df_aulas.empty:
            st.dataframe(df_aulas, use_container_width=True, hide_index=True)