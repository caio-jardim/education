import streamlit as st
import database as db
from datetime import date, time
from modules.ui.core import header_page

def show_page_aulas(id_prof_logado, nome_prof):
    header_page("Gestão de Aulas", "Lançamento e Histórico")
    
    # CSS para garantir que os inputs fiquem brancos (padrão do sistema)
    st.markdown("""
        <style>
            div[data-baseweb="select"] > div {
                background-color: #FFFFFF !important;
                border-color: #D1D1D1 !important;
                color: #1A1A1A !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    tab_lancamento, tab_historico = st.tabs(["📝 Registrar Nova Aula", "📜 Histórico Completo"])
    
    # --- ABA 1: LANÇAR AULA ---
    with tab_lancamento:
        st.markdown("##### Nova Aula")
        
        # Carrega dados
        df_alunos_geral = db.get_saldo_alunos()
        
        # Filtra alunos vinculados a este professor
        try:
            df_links = db.get_vinculos()
            # Normaliza nomes das colunas
            if 'ID Professor' in df_links.columns:
                df_links = df_links.rename(columns={'ID Professor': 'id_prof', 'ID Aluno': 'id_aluno'})
            
            # Filtra vínculos
            meus_vincs = df_links[df_links['id_prof'].astype(str) == str(id_prof_logado)]
            ids_meus = meus_vincs['id_aluno'].astype(str).tolist()
            
            col_id = 'ID Aluno' if 'ID Aluno' in df_alunos_geral.columns else 'id_aluno'
            
            # Se tiver vínculos, filtra. Se não, mostra todos (fallback)
            if ids_meus:
                df_alunos_selectbox = df_alunos_geral[df_alunos_geral[col_id].astype(str).isin(ids_meus)]
            else:
                df_alunos_selectbox = df_alunos_geral
                
        except:
            df_alunos_selectbox = df_alunos_geral # Fallback se der erro no filtro
        
        with st.form("form_aula_prof", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                col_nome = 'Nome Aluno' if 'Nome Aluno' in df_alunos_selectbox.columns else 'nome_aluno'
                lista_alunos = df_alunos_selectbox[col_nome].unique() if not df_alunos_selectbox.empty else []
                
                nome_aluno_selecionado = st.selectbox("Aluno", options=lista_alunos)
                
                # --- DATA E HORÁRIO (COM SELECTBOX) ---
                c_data, c_hora = st.columns(2)
                data_aula = c_data.date_input("Data", date.today(), format="DD/MM/YYYY")
                
                # Gera lista de horários: 07:00 até 22:30 (30 em 30 min)
                lista_horarios = []
                for h in range(7, 23): # 07h até 22h
                    lista_horarios.append(f"{h:02d}:00")
                    if h < 23: # Garante até 22:30
                        lista_horarios.append(f"{h:02d}:30")
                
                # Remove horários pós 22:30
                if "23:00" in lista_horarios: lista_horarios.remove("23:00")
                
                # Padrão: 09:00 ou o primeiro da lista
                idx_padrao = lista_horarios.index("09:00") if "09:00" in lista_horarios else 0
                
                # O Selectbox substitui o time_input problemático
                hora_selecionada_str = c_hora.selectbox("Horário", options=lista_horarios, index=idx_padrao)
            
            with col2:
                duracao = st.number_input("Duração (h)", min_value=0.5, step=0.5, format="%.1f")
                modalidade = st.selectbox("Modalidade", ["Education", "Online", "Casa"])
            
            obs = st.text_area("Conteúdo / Observações")
            
            if st.form_submit_button("✅ Registrar Aula"):
                try:
                    # Recupera ID do Aluno selecionado
                    filtro = df_alunos_geral[df_alunos_geral[col_nome] == nome_aluno_selecionado]
                    
                    if not filtro.empty:
                        col_id_aluno = 'ID Aluno' if 'ID Aluno' in filtro.columns else 'id_aluno'
                        id_aluno_sel = filtro[col_id_aluno].values[0]
                        
                        data_str = data_aula.strftime("%d/%m/%Y")
                        # A hora já vem como string "HH:MM" do selectbox, perfeito para salvar
                        hora_str = hora_selecionada_str 
                        
                        # Salva no banco
                        db.registrar_aula(
                            data_str, 
                            hora_str, 
                            int(id_aluno_sel), 
                            nome_aluno_selecionado, 
                            int(id_prof_logado), 
                            nome_prof, 
                            modalidade, 
                            duracao, 
                            "Realizada" # Professor lança como realizada por padrão
                        )
                        st.success("Aula registrada com sucesso!")
                        # Opcional: st.rerun() para limpar o form visualmente se o clear_on_submit falhar com selectbox
                    else:
                        st.error("Erro: Aluno não encontrado na base de dados.")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

    # --- ABA 2: HISTÓRICO ---
    with tab_historico:
        try:
            df_aulas = db.get_aulas()
            if not df_aulas.empty:
                # Normaliza nomes para filtro
                col_id_prof_aula = 'ID Professor' if 'ID Professor' in df_aulas.columns else 'id_professor'
                
                # Filtra aulas deste professor
                if col_id_prof_aula in df_aulas.columns:
                    # Converte para string para garantir comparação
                    minhas_aulas = df_aulas[df_aulas[col_id_prof_aula].astype(str) == str(id_prof_logado)]
                    
                    # Remove colunas técnicas desnecessárias para o professor ver
                    cols_ocultar = ['Comissão Professor', 'ID Venda', 'ID Vinculo']
                    cols_mostrar = [c for c in minhas_aulas.columns if c not in cols_ocultar]
                    
                    st.dataframe(minhas_aulas[cols_mostrar], use_container_width=True, hide_index=True)
                else:
                    st.dataframe(df_aulas)
            else:
                st.info("Nenhuma aula registrada ainda.")
        except Exception as e:
            st.error(f"Erro ao ler histórico: {e}")