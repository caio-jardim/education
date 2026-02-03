import streamlit as st
from streamlit_option_menu import option_menu
from modules.ui.core import load_css 

# --- IMPORTAÇÃO UNIFICADA (A Grande Mudança) ---
# Agora importamos as funções principais direto do pacote views
from views import show_login, show_professor, show_admin

# --- 1. CONFIGURAÇÃO INICIAL (Deve ser a primeira linha) ---
st.set_page_config(
    page_title="Education Suporte", 
    page_icon="assets/favicon.png", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CARREGAR ESTILO PREMIUM ---
# Injeta o CSS (Fundo Off-White, Fontes, Cards, Sidebar Preta)
load_css()

# --- 3. GESTÃO DE SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['usuario'] = None

# --- 4. ROTEAMENTO PRINCIPAL ---
if not st.session_state['logado']:
    # Tela de Login (Limpa, sem sidebar)
    show_login()

else:
    # --- USUÁRIO LOGADO: CONSTRUÇÃO DA INTERFACE ---
    
    # Recupera dados do usuário
    usuario_atual = st.session_state['usuario']
    nome_exibicao = usuario_atual.get('Nome Usuário', usuario_atual.get('Username', 'Usuário'))
    # Garante que admin/Admin/ADMIN vire 'admin'
    tipo_perfil = str(usuario_atual.get('Tipo Perfil', '')).lower().strip()

    # --- SIDEBAR PREMIUM ---
    with st.sidebar:
        # A. Logo da Empresa
        try:
            st.image("assets/logo.png", use_container_width=True)
        except:
            st.markdown("## Education") # Fallback se não tiver imagem
            
        st.write("") # Espaçamento

        # B. Menu de Navegação (Muda conforme o perfil)
        if tipo_perfil == 'admin':
            selected = option_menu(
                menu_title=None,
                # As opções devem bater EXATAMENTE com os IFs do views/admin/main.py
                options=["Visão Geral", "Cadastros", "Alunos", "Professores", "Vendas", "Financeiro", "Aulas"],
                icons=["grid-fill", "person-badge", "backpack", "people-fill", "tag-fill", "currency-dollar", "mortarboard"],
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#FFFFFF", "font-size": "14px"},
                    "nav-link": {
                        "font-family": "Poppins", "font-size": "15px", 
                        "text-align": "left", "margin": "5px", 
                        "color": "#FFFFFF", "--hover-color": "#333333"
                    },
                    "nav-link-selected": {
                        "background-color": "#2C2C2C", "color": "#C5A065", 
                        "font-weight": "600", "border-left": "3px solid #C5A065"
                    },
                }
            )
        else:
            # Menu Simplificado para Professores
            selected = option_menu(
                menu_title=None,
                # As opções devem bater EXATAMENTE com os IFs do views/professores/main.py
                options=["Meus Alunos", "Minhas Aulas", "Agenda"],
                icons=["people-fill", "mortarboard", "calendar3"],
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#FFFFFF", "font-size": "14px"},
                    "nav-link": {"font-family": "Poppins", "font-size": "15px", "text-align": "left", "margin": "5px", "color": "#FFFFFF", "--hover-color": "#333333"},
                    "nav-link-selected": {"background-color": "#2C2C2C", "color": "#C5A065", "font-weight": "600", "border-left": "3px solid #C5A065"},
                }
            )

        # C. Footer da Sidebar (Perfil + Logout)
        st.markdown("---") # Divisor visual
        
        # Container de perfil estilizado
        st.markdown(
            f"""
            <div style="background-color: #2C2C2C; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                <div style="color: #C5A065; font-size: 12px; font-weight: bold;">LOGADO COMO</div>
                <div style="color: white; font-size: 14px;">{nome_exibicao}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # Botão de Sair
        if st.button("Sair do Sistema", use_container_width=True):
            st.session_state['logado'] = False
            st.session_state['usuario'] = None
            st.rerun()

    # --- ÁREA DE CONTEÚDO PRINCIPAL ---
    # Aqui chamamos as funções importadas diretamente do __init__.py das views
    
    if tipo_perfil == 'admin':
        show_admin(usuario_atual, selected_page=selected)
        
    elif tipo_perfil in ['professor', 'prof']:
        show_professor(usuario_atual, selected_page=selected)
        
    else:
        st.error(f"⚠️ Acesso negado. Perfil não identificado: {tipo_perfil}")