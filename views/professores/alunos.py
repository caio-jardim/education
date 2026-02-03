import streamlit as st
import database as db
from modules.ui.core import header_page, kpi_card

def show_page_alunos(id_prof_logado, nome_prof):
    header_page("Meus Alunos", f"Painel de {nome_prof}")
    
    try:
        # 1. Carrega tabelas necessárias
        df_alunos = db.get_saldo_alunos() # Tabela DASH_Alunos (já calculada)
        
        # Tenta carregar vínculos.
        try:
            df_links = db.get_vinculos() # Tabela LINK_Alunos_Professores
        except AttributeError:
            st.error("⚠️ Função 'db.get_vinculos()' não encontrada.")
            df_links = None

        # 2. Lógica de Filtragem
        df_meus_alunos = df_alunos # Padrão: mostra todos se falhar

        if df_links is not None and not df_links.empty:
            # Normaliza nomes das colunas do LINK
            df_links = df_links.rename(columns={
                'ID Professor': 'id_prof_link',
                'ID Aluno': 'id_aluno_link'
            })
            
            # Filtra apenas linhas onde ID Professor == ID do Usuário Logado
            vinculos_prof = df_links[df_links['id_prof_link'].astype(str) == str(id_prof_logado)]
            
            # Pega a lista de IDs dos alunos vinculados
            ids_meus_alunos = vinculos_prof['id_aluno_link'].astype(str).tolist()
            
            # Filtra a tabela de Alunos usando essa lista de IDs
            col_id_aluno_cad = 'ID Aluno' if 'ID Aluno' in df_alunos.columns else 'id_aluno'
            
            if col_id_aluno_cad in df_alunos.columns:
                df_meus_alunos = df_alunos[df_alunos[col_id_aluno_cad].astype(str).isin(ids_meus_alunos)]
        
        # 3. Exibição dos KPIs e Tabela
        kpi_card("Total de Alunos", str(len(df_meus_alunos)), "icon_alunos.png")
        st.write("")
        
        # Seleção segura de colunas para exibição
        cols_originais = df_meus_alunos.columns.tolist()
        cols_desejadas = ['Nome Aluno', 'Horas Compradas', 'Saldo Disponível']
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