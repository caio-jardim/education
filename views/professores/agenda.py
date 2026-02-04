import streamlit as st
import pandas as pd
import database as db
from modules.ui.core import header_page
from datetime import datetime, date

def show_agenda(id_prof_logado, nome_prof):
    header_page("Minha Agenda", "Próximos compromissos")
    
    # --- CSS LOCAL ---
    st.markdown("""
        <style>
            .time-box {
                background-color: #F0F2F6;
                color: #1A1A1A;
                border: 1px solid #D1D1D1;
                border-radius: 6px;
                padding: 8px 0px;
                text-align: center;
                font-weight: 700;
                font-size: 15px;
                display: block;
                width: 100%;
            }
        </style>
    """, unsafe_allow_html=True)

    try:
        # 1. Carrega Aulas
        df_aulas = db.get_aulas()
        
        if df_aulas.empty:
            st.info("Nenhuma aula encontrada no sistema.")
            return

        # --- CAMADA DE LIMPEZA DE DADOS (A SOLUÇÃO) ---
        # 1. Identifica a coluna de ID do Professor
        col_id_prof = next((c for c in df_aulas.columns if 'id' in c.lower() and 'prof' in c.lower()), 'ID Professor')
        
        # 2. Força o ID para string e remove ".0" (ex: "2.0" vira "2") e espaços
        df_aulas['ID_Prof_Clean'] = df_aulas[col_id_prof].astype(str).str.replace('.0', '', regex=False).str.strip()
        
        # 3. Limpa o Status (remove espaços invisíveis)
        if 'Status' in df_aulas.columns:
            df_aulas['Status'] = df_aulas['Status'].astype(str).str.strip()
        
        # 4. Limpa o ID do Logado também
        id_logado_clean = str(id_prof_logado).replace('.0', '').strip()
        # ----------------------------------------------

        # 2. Filtragem Blindada
        minha_agenda = df_aulas[
            (df_aulas['ID_Prof_Clean'] == id_logado_clean) & 
            (df_aulas['Status'] == 'Agendada')
        ].copy()

        if minha_agenda.empty:
            st.info("📅 Você não possui aulas agendadas pendentes.")
            return

        # 3. Tratamento de Datas para Ordenação
        minha_agenda['Data_Dt'] = pd.to_datetime(minha_agenda['Data'], format="%d/%m/%Y", errors='coerce')
        
        col_ordem = ['Data_Dt']
        if 'Horário' in minha_agenda.columns: col_ordem.append('Horário')
        
        minha_agenda = minha_agenda.sort_values(by=col_ordem)

        # 4. Renderização
        dias_unicos = minha_agenda['Data_Dt'].dropna().unique()

        for dia in dias_unicos:
            dia_str = pd.to_datetime(dia).strftime("%d/%m/%Y")
            dia_nome = pd.to_datetime(dia).strftime("%A")
            mapa_dias = {'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
            dia_pt = mapa_dias.get(dia_nome, dia_nome)
            
            st.markdown(f"#### 🗓️ {dia_str} <span style='font-size:0.7em; color:gray'>({dia_pt})</span>", unsafe_allow_html=True)
            
            aulas_do_dia = minha_agenda[minha_agenda['Data_Dt'] == dia]
            
            for _, row in aulas_do_dia.iterrows():
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([1.5, 4, 2, 2.5])
                    
                    horario = row.get('Horário', '--:--')
                    c1.markdown(f"<div class='time-box'>⏰ {horario}</div>", unsafe_allow_html=True)
                    
                    nome_aluno = row.get('Nome Aluno', 'Aluno')
                    c2.markdown(f"**{nome_aluno}**")
                    c2.caption(f"Modalidade: {row.get('Modalidade', '-')}")
                    
                    duracao = row.get('Duração', '1')
                    c3.write(f"⏳ {duracao}h")
                    
                    with c4:
                        col_ok, col_cancel = st.columns(2)
                        
                        # IDs únicos para botões
                        id_aula = row.get('ID Aula') # Pega o ID da planilha
                        key_ok = f"ok_{id_aula}"
                        key_cancel = f"cancel_{id_aula}"
                        
                        if col_ok.button("✅", key=key_ok, help="Confirmar"):
                            db.atualizar_status_aula(id_aula, "Realizada")
                            
                            try:
                                import database.vendas as db_vendas
                                id_aluno = row.get('ID Aluno', row.get('id_aluno'))
                                # Garante conversão para datetime puro do python
                                dt_obj = pd.to_datetime(dia).to_pydatetime()
                                
                                ativou, msg = db_vendas.processar_primeira_aula(id_aluno, dt_obj)
                                if ativou: st.toast(f"🎉 {msg}", icon="🚀")
                            except: pass
                                
                            st.toast("Aula confirmada!", icon="✅")
                            st.rerun()
                            
                        if col_cancel.button("❌", key=key_cancel, help="Cancelar"):
                            db.atualizar_status_aula(id_aula, "Cancelada c/ Custo")
                            st.toast("Aula cancelada.", icon="🗑️")
                            st.rerun()

    except Exception as e:
        st.error(f"Erro ao carregar agenda: {e}")