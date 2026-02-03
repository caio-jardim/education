import streamlit as st
import database as db
from modules.ui.core import header_page

# Importa as sub-funções locais
from .alunos import show_page_alunos
from .aulas import show_page_aulas

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

    # --- NAVEGAÇÃO / ROTEAMENTO ---

    # 1. MEUS ALUNOS
    if selected_page == "Meus Alunos":
        show_page_alunos(id_prof_logado, nome_prof)

    # 2. MINHAS AULAS
    elif selected_page == "Minhas Aulas":
        show_page_aulas(id_prof_logado, nome_prof)

    # 3. AGENDA
    elif selected_page == "Agenda":
        header_page("Minha Agenda", "Próximas aulas")
        st.info("🚧 Em desenvolvimento. A agenda futura será exibida aqui.")