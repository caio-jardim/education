import streamlit as st
import database as db
from datetime import date
from modules.ui.core import header_page, kpi_card

def show_professor(usuario, selected_page):
    
    # --- 1. RECUPERAÇÃO SEGURA DO ID DO PROFESSOR ---
    id_prof_logado = usuario.get('id_vinculo') or usuario.get('ID Vinculo') or usuario.get('ID Vínculo')
    
    if not id_prof_logado:
        st.error("🚫 Erro de Cadastro: Seu usuário não possui um 'ID Vínculo' definido.")
        return

    # --- 2. BUSCA DADOS DO PROFESSOR ---
    try:
        df_professores = db.get_professores()
        
        # Renomeia para garantir compatibilidade
        df_professores = df_professores.rename(columns={
            'ID Professor': 'id_prof',
            'Nome Professor': 'nome_prof',
            'Status': 'status'
        })

        if 'id_prof' not in df_professores.columns:
            st.error("Erro técnico: Coluna 'ID Professor' não encontrada na planilha CAD_Professores.")
            return

        # Filtra o Professor logado
        meus_dados = df_professores[df_professores['id_prof'].astype(str) == str(id_prof_logado)]
        
        if meus_dados.empty:
            st.warning(f"⚠️ O ID {id_prof_logado} está no login, mas não achei na aba CAD_Professores.")
            return

        nome_prof = meus_dados.iloc[0]['nome_prof']
        
    except Exception as e:
        st.error(f"Erro de conexão com banco de professores: {e}")
        return

    # --- NAVEGAÇÃO ---

    # 1. MEUS ALUNOS (COM FILTRO DE VÍNCULO)
    if selected_page == "Meus Alunos":
        header_page("Meus Alunos", f"Painel de {nome_prof}")
        
        try:
            # 1. Carrega tabelas necessárias
            df_alunos = db.get_saldo_alunos() # Tabela CAD_Alunos
            
            # Tenta carregar vínculos. Se a função não existir, avisa.
            try:
                df_links = db.get_vinculos() # Tabela LINK_Alunos_Professores
            except AttributeError:
                st.error("⚠️ Função 'db.get_vinculos()' não encontrada. Adicione-a no database.py.")
                df_links = None

            # 2. Lógica de Filtragem
            df_meus_alunos = df_alunos # Padrão: mostra todos se falhar

            if df_links is not None and not df_links.empty:
                # Normaliza nomes das colunas do LINK
                # Garante que estamos lendo as colunas certas do arquivo que você mandou
                df_links = df_links.rename(columns={
                    'ID Professor': 'id_prof_link',
                    'ID Aluno': 'id_aluno_link'
                })
                
                # Filtra apenas linhas onde ID Professor == ID do Usuário Logado
                # Convertendo para string para evitar erros (1 vs "1")
                vinculos_prof = df_links[df_links['id_prof_link'].astype(str) == str(id_prof_logado)]
                
                # Pega a lista de IDs dos alunos vinculados
                ids_meus_alunos = vinculos_prof['id_aluno_link'].astype(str).tolist()
                
                # Filtra a tabela de Alunos usando essa lista de IDs
                # Precisamos saber o nome da coluna ID em CAD_Alunos (Geralmente 'ID Aluno')
                col_id_aluno_cad = 'ID Aluno' if 'ID Aluno' in df_alunos.columns else 'id_aluno'
                
                if col_id_aluno_cad in df_alunos.columns:
                    df_meus_alunos = df_alunos[df_alunos[col_id_aluno_cad].astype(str).isin(ids_meus_alunos)]
            
            # 3. Exibição dos KPIs e Tabela
            kpi_card("Total de Alunos", str(len(df_meus_alunos)), "icon_alunos.png")
            st.write("")
            
            # Seleção segura de colunas para exibição
            cols_originais = df_meus_alunos.columns.tolist()
            cols_desejadas = ['Nome Aluno', 'Série', 'Escola', 'Saldo Horas', 'Status']
            cols_finais = [c for c in cols_desejadas if c in cols_originais]
            
            if not cols_finais: cols_finais = cols_originais 
            
            if not df_meus_alunos.empty:
                st.dataframe(
                    df_meus_alunos[cols_finais], 
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Você ainda não tem alunos vinculados.")
                
        except Exception as e:
            st.error(f"Erro ao carregar alunos: {e}")

    # 2. MINHAS AULAS
    elif selected_page == "Minhas Aulas":
        header_page("Gestão de Aulas", "Lançamento e Histórico")
        
        tab_lancamento, tab_historico = st.tabs(["📝 Registrar Nova Aula", "📜 Histórico Completo"])
        
        # --- ABA 1: LANÇAR AULA ---
        with tab_lancamento:
            st.markdown("##### Nova Aula")
            
            # Carrega SOMENTE os alunos do professor para o selectbox
            # (Reaproveitamos a lógica de filtro se quiser, ou carregamos tudo)
            # Para facilitar, vou carregar todos, mas o ideal seria filtrar também
            df_alunos_geral = db.get_saldo_alunos()
            
            # Tenta filtrar também no selectbox para facilitar pro professor
            # (Lógica simplificada repetida aqui ou poderia ser função)
            try:
                df_links = db.get_vinculos()
                df_links = df_links.rename(columns={'ID Professor': 'id_prof', 'ID Aluno': 'id_aluno'})
                meus_vincs = df_links[df_links['id_prof'].astype(str) == str(id_prof_logado)]
                ids_meus = meus_vincs['id_aluno'].astype(str).tolist()
                
                col_id = 'ID Aluno' if 'ID Aluno' in df_alunos_geral.columns else 'id_aluno'
                df_alunos_selectbox = df_alunos_geral[df_alunos_geral[col_id].astype(str).isin(ids_meus)]
            except:
                df_alunos_selectbox = df_alunos_geral # Fallback se der erro
            
            with st.form("form_aula_prof", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    col_nome = 'Nome Aluno' if 'Nome Aluno' in df_alunos_selectbox.columns else 'nome_aluno'
                    lista_alunos = df_alunos_selectbox[col_nome].unique() if not df_alunos_selectbox.empty else []
                    
                    nome_aluno_selecionado = st.selectbox("Aluno", options=lista_alunos)
                    data_aula = st.date_input("Data", date.today(), format="DD/MM/YYYY")
                
                with col2:
                    duracao = st.number_input("Duração (h)", min_value=0.5, step=0.5, format="%.1f")
                    modalidade = st.selectbox("Modalidade", ["Education", "Online", "Casa"])
                
                obs = st.text_area("Conteúdo / Observações")
                
                if st.form_submit_button("✅ Registrar Aula"):
                    try:
                        filtro = df_alunos_geral[df_alunos_geral[col_nome] == nome_aluno_selecionado]
                        if not filtro.empty:
                            col_id_aluno = 'ID Aluno' if 'ID Aluno' in filtro.columns else 'id_aluno'
                            id_aluno_sel = filtro[col_id_aluno].values[0]
                            data_str = data_aula.strftime("%d/%m/%Y")
                            
                            db.registrar_aula(
                                data_str, int(id_aluno_sel), nome_aluno_selecionado, 
                                int(id_prof_logado), nome_prof, modalidade, duracao, obs
                            )
                            st.success("Aula registrada!")
                        else:
                            st.error("Aluno não encontrado.")
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

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
                    st.info("Nenhuma aula registrada.")
            except Exception as e:
                st.error(f"Erro ao ler histórico: {e}")

    # 3. AGENDA
    elif selected_page == "Agenda":
        header_page("Minha Agenda", "Próximas aulas")
        st.info("🚧 Em desenvolvimento.")