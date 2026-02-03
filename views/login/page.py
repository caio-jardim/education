import streamlit as st
import database as db
import time

def show_login():
    # Espaçamento vertical para descer um pouco o conteúdo (fica mais elegante)
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    
    # --- LAYOUT DE 3 COLUNAS (Para centralizar o Login) ---
    # [Espaço Vazio] [LOGIN] [Espaço Vazio]
    col_esq, col_centro, col_dir = st.columns([1, 1.2, 1]) 

    with col_centro:
        # 1. LOGO DA EMPRESA
        # use_container_width ajusta a logo à largura da coluna central
        st.image("assets/logo1.png", use_container_width=True) 
        
        # 2. TEXTO DE BOAS-VINDAS (HTML Centralizado)
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 30px;">
                <h3 style="color: #1A1A1A; font-family: 'Poppins', sans-serif;">Bem-vindo de volta!</h3>
                <p style="color: #666; font-size: 14px;">Insira suas credenciais para acessar o painel.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # 3. FORMULÁRIO DE LOGIN
        with st.form("login_form"):
            user = st.text_input("Usuário", placeholder="Digite seu usuário")
            password = st.text_input("Senha", type="password", placeholder="••••••")
            
            # Espaço entre inputs e botão
            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
            
            # Botão Primário (Vai pegar o estilo preto/bege do CSS)
            submit = st.form_submit_button("Acessar Sistema", type="primary")
            
            if submit:
                # Validação Básica
                if not user or not password:
                    st.warning("⚠️ Preencha todos os campos.")
                    return

                try:
                    df_users = db.get_usuarios()
                    if df_users.empty:
                        st.error("Erro Crítico: Banco de dados de usuários vazio.")
                        return

                    # Normalização de Colunas
                    col_user = 'Username' if 'Username' in df_users.columns else 'username'
                    col_pass = 'Password' if 'Password' in df_users.columns else 'password'

                    # Limpeza de Inputs
                    user_input = user.strip()
                    pass_input = password.strip()

                    # Verificação
                    usuario_encontrado = df_users[
                        (df_users[col_user].astype(str).str.strip() == user_input) & 
                        (df_users[col_pass].astype(str).str.strip() == pass_input)
                    ]
                    
                    if not usuario_encontrado.empty:
                        # SUCESSO
                        msg_placeholder = st.empty()
                        msg_placeholder.success("Login realizado com sucesso!")
                        
                        st.session_state['logado'] = True
                        st.session_state['usuario'] = usuario_encontrado.iloc[0].to_dict()
                        
                        time.sleep(1) # Pausa dramática elegante
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")
                        
                except Exception as e:
                    st.error(f"Erro ao validar login: {e}")

    # Rodapé Discreto (Opcional)
    st.markdown(
        """
        <div style="text-align: center; margin-top: 50px; color: #BBB; font-size: 12px;">
            Education Suporte © 2026 • Sistema de Gestão Escolar
        </div>
        """, 
        unsafe_allow_html=True
    )

def logout():
    st.session_state['logado'] = False
    st.session_state['usuario'] = None
    st.rerun()