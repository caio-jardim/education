import streamlit as st
import database as db
import database.vendas as db_vendas # <--- Mantido o import importante
from modules.ui import core
from datetime import date, datetime, timedelta, time
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
import pandas as pd
import time as tm

def show_gestao_aulas():
    # --- CSS: LAYOUT DO FORMULÁRIO ---
    st.markdown("""
        <style>
            div[data-testid="stToastContainer"] { top: 80px; right: 20px; bottom: unset; left: unset; align-items: flex-end; }
            div[data-testid="stForm"] { border: none !important; box-shadow: none !important; background-color: transparent !important; padding: 0px !important; }
            div[data-testid="stForm"] > div:first-child { padding-top: 0px !important; margin-top: -10px !important; }
            .time-box { background-color: #F0F2F6 !important; color: #1A1A1A !important; border: 1px solid #D1D1D1; border-radius: 6px; padding: 8px 0px; text-align: center; font-weight: 700; font-size: 15px; display: block; width: 100%; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### 📅 Gestão de Aulas")
    
    tab_agenda, tab_novo, tab_lista = st.tabs(["🗓️ Agenda Dinâmica", "➕ Novo Lançamento", "📜 Histórico"])
    
    df_aulas = db.get_aulas()
    
    # --- TAB 1: AGENDA ---
    with tab_agenda:
        if not df_aulas.empty and 'Status' in df_aulas.columns:
            df_agendadas = df_aulas[df_aulas['Status'] == 'Agendada'].copy()
            if not df_agendadas.empty:
                df_agendadas['Data_Dt'] = pd.to_datetime(df_agendadas['Data'], format="%d/%m/%Y", errors='coerce')
                col_ordem = ['Data_Dt']
                if 'Horário' in df_agendadas.columns: col_ordem.append('Horário')
                df_agendadas = df_agendadas.sort_values(by=col_ordem)
                
                dias_unicos = df_agendadas['Data_Dt'].dropna().unique()
                
                for dia in dias_unicos:
                    dia_str = pd.to_datetime(dia).strftime("%d/%m/%Y")
                    dia_nome = pd.to_datetime(dia).strftime("%A")
                    mapa = {'Monday':'Segunda', 'Tuesday':'Terça', 'Wednesday':'Quarta', 'Thursday':'Quinta', 'Friday':'Sexta', 'Saturday':'Sábado', 'Sunday':'Domingo'}
                    dia_pt = mapa.get(dia_nome, dia_nome)

                    st.markdown(f"##### 📆 {dia_str} <span style='color:gray; font-size:0.8em'>({dia_pt})</span>", unsafe_allow_html=True)
                    aulas_dia = df_agendadas[df_agendadas['Data_Dt'] == dia]
                    
                    for _, row in aulas_dia.iterrows():
                        with st.container(border=True):
                            c1, c2, c3, c4 = st.columns([1.5, 4, 2, 2])
                            horario = row.get('Horário', '00:00')
                            c1.markdown(f"<div class='time-box'>⏰ {horario}</div>", unsafe_allow_html=True)
                            c2.markdown(f"**{row['Nome Aluno']}**")
                            c2.caption(f"Prof. {row['Nome Professor']}")
                            c3.caption(f"{row['Modalidade']} • {row['Duração']}h")
                            with c4:
                                ca, cb = st.columns(2)
                                if ca.button("✅", key=f"ok_{row['ID Aula']}", help="Confirmar"):
                                    db.atualizar_status_aula(row['ID Aula'], "Realizada")
                                    try:
                                        db_vendas.processar_primeira_aula(row['ID Aluno'], pd.to_datetime(row['Data'], format="%d/%m/%Y"))
                                    except: pass
                                    st.rerun()
                                if cb.button("❌", key=f"cancel_{row['ID Aula']}", help="Cancelar"):
                                    db.atualizar_status_aula(row['ID Aula'], "Cancelada c/ Custo")
                                    st.rerun()
            else:
                st.info("Nenhuma aula futura na agenda.")
        else:
            st.info("Sem dados de aulas.")

    # --- TAB 2: NOVO LANÇAMENTO ---
    with tab_novo:
        df_alunos = db.get_alunos()
        df_profs = db.get_professores()
        mapa_alunos = dict(zip(df_alunos['Nome Aluno'], df_alunos['ID Aluno'])) if not df_alunos.empty else {}
        mapa_profs = dict(zip(df_profs['Nome Professor'], df_profs['ID Professor'])) if not df_profs.empty else {}
        
        with st.form("form_aula_inteligente", clear_on_submit=False):
            c_icon, c_title = st.columns([0.5, 10])
            with c_icon: st.markdown("📝")
            with c_title: st.markdown("### Dados da Aula")

            tipo_registro = st.radio("O que deseja fazer?", ["Agendar Aula Futura", "Registrar Aula Realizada"], horizontal=True)
            status_automatico = "Agendada" if tipo_registro == "Agendar Aula Futura" else "Realizada"
            st.markdown("---")
            
            c1, c2, c3 = st.columns(3)
            opcoes_alunos = ["-- Selecione um Aluno --"] + list(mapa_alunos.keys()) if mapa_alunos else ["Sem alunos"]
            opcoes_profs = ["-- Selecione um Professor --"] + list(mapa_profs.keys()) if mapa_profs else ["Sem professores"]
            
            aluno = c1.selectbox("Aluno", options=opcoes_alunos) if mapa_alunos else c1.warning("Sem alunos")
            prof = c2.selectbox("Professor", options=opcoes_profs) if mapa_profs else c2.warning("Sem professores")
            modalidade = c3.selectbox("Modalidade", ["-- Selecione --", "Online", "Education", "Casa"])
            
            c4, c5, c6 = st.columns(3)
            data_inicio = c4.date_input("Data", value=None, format="DD/MM/YYYY")
            
            lista_horarios = ["-- Selecione --"]
            for h in range(7, 23):
                lista_horarios.append(f"{h:02d}:00")
                if h < 23: lista_horarios.append(f"{h:02d}:30")
            if "23:00" in lista_horarios: lista_horarios.remove("23:00")
            if "23:30" in lista_horarios: lista_horarios.remove("23:30")
            
            hora_selecionada_str = c5.selectbox("Horário", options=lista_horarios, index=0)
            
            duracao = c6.number_input("Duração (h)", value=None, step=0.5, min_value=0.5)
            
            st.markdown("###### 🔁 Repetição")
            col_rep, col_qtd = st.columns([2, 1])
            tipo_rep = col_rep.selectbox("Frequência", ["-- Selecione --", "Uma única vez", "Diariamente", "Semanalmente", "Mensalmente"], index=0)
            
            qtd_repeticoes = 1
            if tipo_rep != "-- Selecione --" and tipo_rep != "Uma única vez":
                qtd_repeticoes = col_qtd.number_input("Repetir por quantas vezes?", min_value=2, value=4, step=1)

            datas_geradas = [data_inicio] if data_inicio else []
            if tipo_rep != "-- Selecione --" and tipo_rep != "Uma única vez" and data_inicio and hora_selecionada_str != "-- Selecione --":
                freq_map = {"Diariamente": DAILY, "Semanalmente": WEEKLY, "Mensalmente": MONTHLY}
                try:
                    h_sel, m_sel = map(int, hora_selecionada_str.split(':'))
                    hora_inicio = time(h_sel, m_sel)
                    datas_geradas = list(rrule(freq=freq_map[tipo_rep], dtstart=datetime.combine(data_inicio, hora_inicio), count=qtd_repeticoes))
                    datas_geradas = [d.date() for d in datas_geradas]
                except Exception as e: st.error(f"Erro datas: {e}")
            elif tipo_rep == "Uma única vez" and data_inicio and hora_selecionada_str != "-- Selecione --":
                datas_geradas = [data_inicio]

            if len(datas_geradas) > 1:
                st.caption(f"ℹ️ Serão criados **{len(datas_geradas)} registros** com status **'{status_automatico}'**.")

            st.markdown("<br>", unsafe_allow_html=True)
            
            c_btn_save, c_btn_cancel, c_void = st.columns([1.5, 1.5, 6])
            btn_disabled = not (opcoes_alunos and opcoes_profs)
            
            with c_btn_save:
                confirmar = st.form_submit_button(f"Salvar", disabled=btn_disabled)
            with c_btn_cancel:
                cancelar = st.form_submit_button("Cancelar", type="secondary")
            
            if confirmar and not btn_disabled:
                if not aluno or not prof or aluno.startswith("--") or prof.startswith("--") or modalidade.startswith("--"):
                    core.notify_warning("⚠️ Selecione Aluno, Professor e Modalidade antes de salvar.")
                elif not data_inicio or hora_selecionada_str.startswith("--") or duracao is None or duracao == 0 or tipo_rep.startswith("--"):
                    core.notify_warning("⚠️ Preencha Data, Horário, Duração e Frequência antes de salvar.")
                elif not datas_geradas:
                    core.notify_warning("⚠️ Ocorreu um erro ao processar as datas. Verifique os valores.")
                else:
                    try:
                        id_a = mapa_alunos[aluno]
                        id_p = mapa_profs[prof]
                        hora_str = hora_selecionada_str 
                        
                        val_hora = 0.0
                        dados_prof = df_profs[df_profs['ID Professor'].astype(str) == str(id_p)]
                        if not dados_prof.empty:
                            linha_p = dados_prof.iloc[0]
                            termo = "Education" if modalidade == "Education" else modalidade.split()[0]
                            for col in linha_p.keys():
                                if termo.lower() in col.lower():
                                    v = linha_p[col]
                                    if isinstance(v, (int, float)): val_hora = float(v)
                                    else: 
                                        s = str(v).replace('R$', '').replace('.', '').replace(',', '.').strip()
                                        val_hora = float(s) if s else 0.0
                                    break
                        
                        comissao = val_hora * duracao
                        lote = []
                        for d in datas_geradas:
                            lote.append([d.strftime("%d/%m/%Y"), hora_str, id_a, aluno, id_p, prof, modalidade, str(duracao).replace('.', ','), status_automatico, comissao])
                        
                        sucesso, msg = db.registrar_lote_aulas(lote)
                        
                        if sucesso:
                            if datas_geradas:
                                try:
                                    ativou, msg_venda = db_vendas.processar_primeira_aula(id_a, datas_geradas[0])
                                    if ativou:
                                        core.notify_success(msg_venda)
                                except Exception as e_venda:
                                    print(f"Erro ao processar pacote: {e_venda}")

                            core.notify_success(msg)
                            st.cache_data.clear()
                            tm.sleep(1) 
                            st.rerun()
                    except Exception as e:
                        core.notify_error(f"Erro: {e}")
            
            if cancelar: st.rerun()

    # --- TAB 3: HISTÓRICO (FILTROS: MÊS, PROFESSOR, ALUNO) ---
    with tab_lista:
        st.markdown("##### 📜 Histórico de Aulas")
        
        if not df_aulas.empty:
            # 1. Copia para não afetar o cache original
            df_hist = df_aulas.copy()
            
            # 2. Converte Data
            df_hist['Data_Dt'] = pd.to_datetime(df_hist['Data'], format="%d/%m/%Y", errors='coerce')
            df_hist = df_hist.dropna(subset=['Data_Dt']) # Remove datas inválidas se houver
            df_hist = df_hist.sort_values(by='Data_Dt', ascending=False)
            
            # 3. Cria Coluna de Filtro (Mês/Ano)
            # Mapa PT-BR Manual para garantir a língua independente do servidor
            meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
            
            df_hist['Mes_Filtro'] = df_hist['Data_Dt'].apply(lambda x: f"{meses_pt[x.month]}/{x.year}")
            
            # 4. Prepara Opções de Filtro
            opcoes_meses = sorted(df_hist['Mes_Filtro'].unique().tolist(), reverse=True)
            opcoes_profs = ['📋 Todos os Professores'] + sorted([p for p in df_hist['Nome Professor'].unique().tolist() if pd.notna(p)])
            opcoes_alunos = ['📋 Todos os Alunos'] + sorted([a for a in df_hist['Nome Aluno'].unique().tolist() if pd.notna(a)])
            
            # 5. Cria Layout de Filtros em 3 Colunas
            c_mes, c_prof, c_aluno = st.columns(3)
            
            with c_mes:
                mes_selecionado = st.selectbox("📅 Mês:", options=opcoes_meses, key="filtro_mes_historico")
            
            with c_prof:
                prof_selecionado = st.selectbox("👨‍🏫 Professor:", options=opcoes_profs, key="filtro_prof_historico")
            
            with c_aluno:
                aluno_selecionado = st.selectbox("📚 Aluno:", options=opcoes_alunos, key="filtro_aluno_historico")
            
            # 6. Filtra Dados baseado nos Selectbox
            df_exibicao = df_hist[df_hist['Mes_Filtro'] == mes_selecionado].copy()
            
            if not prof_selecionado.startswith('📋'):
                df_exibicao = df_exibicao[df_exibicao['Nome Professor'] == prof_selecionado]
            
            if not aluno_selecionado.startswith('📋'):
                df_exibicao = df_exibicao[df_exibicao['Nome Aluno'] == aluno_selecionado]
            
            # 7. Formata Comissão no padrão brasileiro
            def _fmt_comissao(v):
                try:
                    s = str(v).replace('R$', '').replace('.', '').replace(',', '.').strip()
                    n = float(s) if s else 0.0
                    return f"R$ {n:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                except:
                    return v

            if 'Comissão' in df_exibicao.columns:
                df_exibicao['Comissão'] = df_exibicao['Comissão'].apply(_fmt_comissao)

            # 8. Exibe Tabela Limpa (Remove colunas auxiliares)
            cols_ocultar = ['Data_Dt', 'Mes_Filtro', 'key']
            st.dataframe(
                df_exibicao.drop(columns=[c for c in cols_ocultar if c in df_exibicao.columns]), 
                use_container_width=True, 
                hide_index=True
            )
            
            # 8. Rodapé com Informações
            st.divider()
            col_info, col_vazio = st.columns([3, 2])
            
            with col_info:
                info_text = f"📊 **{len(df_exibicao)}** aulas"
                info_text += f" em {mes_selecionado}"
                
                if not prof_selecionado.startswith('📋'):
                    info_text += f" • Prof. {prof_selecionado}"
                
                if not aluno_selecionado.startswith('📋'):
                    info_text += f" • Aluno {aluno_selecionado}"
                
                st.caption(info_text)
            
        else:
            st.info("Nenhuma aula registrada no sistema.")