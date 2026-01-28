import streamlit as st
import base64
import os

# --- 1. FUNÇÕES AUXILIARES ---

def load_css():
    """Carrega o CSS global e aplica correções visuais forçadas"""
    caminho_css = "assets/style.css"
    
    # Validação de arquivo
    if not os.path.exists(caminho_css):
        st.error(f"Arquivo de estilo não encontrado: {caminho_css}")
        return

    try:
        with open(caminho_css, encoding="utf-8") as f:
            css_content = f.read()
            
        # CSS INJETADO EXTRA (Para matar o keyboard_double de vez)
        css_extra = """
        <style>
            /* Esconde botão de fechar sidebar e o texto bugado */
            [data-testid="stSidebarCollapseButton"] { display: none !important; }
            [data-testid="stSidebarCollapsedControl"] { display: none !important; }
            
            /* Ajuste fino da Logo */
            [data-testid="stSidebar"] img {
                margin-top: -20px !important; /* Sobe a logo */
                padding: 0px !important;
            }
        </style>
        """
        
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        st.markdown(css_extra, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Erro ao carregar CSS: {e}")

def get_img_as_base64(file_path):
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 2. COMPONENTES VISUAIS (WIDGETS) ---

def kpi_card(titulo, valor, nome_arquivo_icone):
    # Procura na pasta assets
    caminho = f"assets/{nome_arquivo_icone}"
    img_b64 = get_img_as_base64(caminho)
    
    img_html = f'<img src="data:image/png;base64,{img_b64}" class="kpi-icon-img">' if img_b64 else ""
    
    html = f"""
    <div class="kpi-card">
        {img_html}
        <div class="kpi-title">{titulo}</div>
        <div class="kpi-value">{valor}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def header_page(titulo, subheader=None):
    st.markdown(f"""
        <div style="margin-bottom: 25px">
            <h1 style='color: #1A1A1A; font-size: 32px; margin: 0;'>{titulo}</h1>
            <p style='color: #666; font-size: 16px; margin: 5px 0 0 0;'>{subheader if subheader else ''}</p>
            <hr style='border: 0; border-top: 1px solid #E0E0E0; margin-top: 15px;'>
        </div>
    """, unsafe_allow_html=True)