import streamlit as st
import base64
import os

# --- 1. FUNÇÕES AUXILIARES DE SISTEMA ---

def load_css():
    """
    Carrega o CSS global (assets/style.css) E aplica a correção do Toast.
    """
    # 1. Carrega o arquivo externo (Onde está o tema Branco/Bege)
    caminho_css = "assets/style.css"
    css_content = ""
    
    if os.path.exists(caminho_css):
        try:
            with open(caminho_css, encoding="utf-8") as f:
                css_content = f.read()
        except Exception as e:
            st.error(f"Erro ao ler style.css: {e}")
    else:
        st.warning(f"Arquivo de estilo não encontrado: {caminho_css}")

    # 2. Define o CSS do Toast (Pop-up) para ficar no topo direito
    css_toast = """
    /* --- CONFIGURAÇÃO DO TOAST (POP-UP) --- */
    div[data-testid="stToastContainer"] {
        top: 80px !important;      /* Fica no topo */
        right: 20px !important;    /* Canto direito */
        bottom: unset !important;  /* Solta de baixo */
        left: unset !important;    /* Solta da esquerda */
        align-items: flex-end !important;
        z-index: 99999 !important; /* Fica sobre tudo */
    }
    
    /* Estilo do Card do Toast */
    div[data-testid="stToast"] {
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        background-color: #FFFFFF !important; /* Garante fundo branco no toast */
        color: #1A1A1A !important;
        border: 1px solid #E0E0E0;
    }
    """

    # 3. Injeta TUDO junto (Estilo do Arquivo + Estilo do Toast)
    st.markdown(f"<style>{css_content}\n{css_toast}</style>", unsafe_allow_html=True)

def get_img_as_base64(file_path):
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 2. COMPONENTES VISUAIS (WIDGETS) ---

def kpi_card(titulo, valor, nome_arquivo_icone):
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

# --- 3. FUNÇÕES DE NOTIFICAÇÃO PADRONIZADAS (TOASTS) ---

def notify_success(msg):
    """Gera um Toast verde de sucesso no canto superior direito."""
    st.toast(msg, icon="✅")

def notify_error(msg):
    """Gera um Toast vermelho de erro no canto superior direito."""
    st.toast(str(msg), icon="❌")

def notify_warning(msg):
    """Gera um Toast amarelo de aviso."""
    st.toast(msg, icon="⚠️")