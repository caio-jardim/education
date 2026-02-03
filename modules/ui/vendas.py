import streamlit as st
import database as db
from modules.ui import core 
from datetime import date

def form_renovacao_pacote():
    # --- CSS IDÊNTICO AO DE NOVO ALUNO ---
    st.markdown("""
        <style>
            /* 1. Formulário Transparente (Sem borda e sem fundo preto) */
            div[data-testid="stForm"] {
                border: none !important;
                box-shadow: none !important;
                background-color: transparent !important;
                padding: 0px !important;
            }
            /* 2. REDUÇÃO DE ESPAÇO DO TÍTULO */
            div[data-testid="stForm"] > div:first-child {
                padding-top: 0px !important;
                margin-top: -20px !important; 
            }
        </style>
    """, unsafe_allow_html=True)

    # Carregamento de Dados
    df_alunos = db.get_alunos()
    if df_alunos.empty:
        st.warning("Nenhum aluno cadastrado no sistema.")
        return

    col_nome = 'Nome Aluno' if 'Nome Aluno' in df_alunos.columns else 'nome_aluno'
    col_id = 'ID Aluno' if 'ID Aluno' in df_alunos.columns else 'id_aluno'
    
    try:
        mapa_alunos = dict(zip(df_alunos[col_nome], df_alunos[col_id]))
    except KeyError:
        st.error("Erro nas colunas do arquivo CAD_Alunos.")
        return

    # --- INÍCIO DO FORMULÁRIO (CLEAN) ---
    with st.form("form_venda_avulsa", clear_on_submit=True, enter_to_submit=False):
        
        # CABEÇALHO COM ÍCONE (Igual Novo Aluno)
        c_icon, c_title = st.columns([0.5, 10])
        with c_icon:
            # Reutilizei o ícone de pacote pois faz sentido para vendas
            st.image("assets/icon_novo_pacote.png", width=45) 
        with c_title:
            st.markdown("### Nova Venda / Renovação")

        # LINHA 1: ALUNO E HORAS
        c1, c2 = st.columns([3, 1])
        with c1:
            nome_sel = st.selectbox("Aluno", options=df_alunos[col_nome].unique())
        with c2:
            qtd_horas = st.number_input("Qtd Horas", min_value=1.0, step=0.5, format="%.1f")
        
        # LINHA 2: DATAS E PAGAMENTO
        c3, c4, c5 = st.columns(3)
        with c3:
            data_contrato = st.date_input("Data da Venda", format="DD/MM/YYYY")
        with c4:
            st.write("") 
            st.write("") # Espaçamento para alinhar checkbox
            pagou = st.checkbox("Pagamento Confirmado", value=True)
        with c5:
            dt_pag = st.date_input("Data do Pagamento", value=date.today(), format="DD/MM/YYYY") if pagou else None

        st.markdown("<br>", unsafe_allow_html=True)

        # SEÇÃO DE VALOR (Separada visualmente)
        c_icon2, c_title2 = st.columns([0.5, 10])
        with c_icon2:
             # Ícone de dinheiro/vendas (fallback genérico se não tiver imagem específica)
             st.markdown("💰") 
        with c_title2:
            st.markdown("### Detalhes Financeiros")

        c_check, c_val, c_void = st.columns([1.5, 2, 3])
        with c_check:
            st.write("")
            st.write("")
            usar_manual = st.checkbox("Definir valor manual")
        
        with c_val:
            valor_manual_input = st.number_input(
                "Valor Total (R$)", 
                min_value=0.0, 
                step=10.0, 
                format="%.2f"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- RODAPÉ: BOTÕES (Igual Novo Aluno) ---
        c_btn_save, c_btn_cancel, c_void_btn = st.columns([1.5, 1.5, 6])
        
        with c_btn_save:
            confirmar = st.form_submit_button("Confirmar")
        
        with c_btn_cancel:
            cancelar = st.form_submit_button("Cancelar", type="secondary")

        # --- LÓGICA ---
        if confirmar:
            id_aluno = mapa_alunos[nome_sel]
            contrato_str = data_contrato.strftime("%d/%m/%Y")
            pag_str = dt_pag.strftime("%d/%m/%Y") if dt_pag else ""
            
            val_final = valor_manual_input if usar_manual else None
            
            try:
                sucesso, msg = db.registrar_venda_automatica(
                    id_aluno, nome_sel, qtd_horas, "Pix", contrato_str, pag_str, valor_manual=val_final
                )
                
                if sucesso:
                    core.notify_success(msg)
                    st.cache_data.clear()
                    # Pequeno delay para exibir a notificação antes de recarregar
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    core.notify_warning(msg)
            except Exception as e:
                core.notify_error(f"Erro técnico: {e}")
        
        if cancelar:
            st.rerun()