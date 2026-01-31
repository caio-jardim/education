import streamlit as st
import database as db
from modules.ui import core 
from datetime import date

def form_renovacao_pacote():
    # CSS Toast
    st.markdown("""<style>div[data-testid="stToastContainer"] {top: 80px; right: 20px; bottom: unset; left: unset; align-items: flex-end;}</style>""", unsafe_allow_html=True)

    st.markdown("#### Nova Venda / Renovação")
    
    df_alunos = db.get_alunos()
    if df_alunos.empty:
        st.warning("Nenhum aluno cadastrado no sistema.")
        return

    # Mapeamentos
    col_nome = 'Nome Aluno' if 'Nome Aluno' in df_alunos.columns else 'nome_aluno'
    col_id = 'ID Aluno' if 'ID Aluno' in df_alunos.columns else 'id_aluno'
    
    try:
        mapa_alunos = dict(zip(df_alunos[col_nome], df_alunos[col_id]))
    except KeyError:
        st.error("Erro nas colunas do arquivo CAD_Alunos.")
        return

    with st.form("form_venda_avulsa", clear_on_submit=True, enter_to_submit=False):
        col_sel, col_hr = st.columns([2, 1])
        with col_sel:
            nome_sel = st.selectbox("Selecione o Aluno", options=df_alunos[col_nome].unique())
        with col_hr:
            qtd_horas = st.number_input("Qtd Horas", min_value=1.0, step=0.5, format="%.1f")
            
        c1, c2, c3 = st.columns(3)
        data_contrato = c1.date_input("Data Venda", format="DD/MM/YYYY")
        pagou = c2.checkbox("Pagamento confirmado?", value=True)
        dt_pag = c3.date_input("Data Pagamento", value=date.today(), format="DD/MM/YYYY") if pagou else None

        st.markdown("---")
        st.markdown("##### Valor da Venda")
        
        # Layout Lado a Lado: Checkbox (Ativador) | Input (Valor)
        col_check, col_val = st.columns([1, 2])
        
        with col_check:
            st.markdown("<br>", unsafe_allow_html=True) # Pequeno ajuste de alinhamento vertical
            # Checkbox controla APENAS a lógica, não esconde o campo (para não travar)
            usar_manual = st.checkbox("Inserir valor manualmente?")
            
        with col_val:
            valor_manual_input = st.number_input(
                "Valor Total (R$)", 
                min_value=0.0, 
                step=10.0, 
                format="%.2f",
                help="Este valor só será usado se a caixa ao lado estiver marcada."
            )

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- BOTÕES PEQUENOS À ESQUERDA ---
        # Criamos colunas para "espremer" os botões na esquerda
        c_btn1, c_btn2, c_space = st.columns([1, 1, 5])
        
        with c_btn1:
            # Botão Confirmar
            confirmar = st.form_submit_button("✅ Confirmar")
            
        with c_btn2:
            # Botão Cancelar (Serve para limpar o form)
            cancelar = st.form_submit_button("❌ Cancelar")

        # --- LÓGICA DE SUBMISSÃO ---
        if confirmar:
            id_aluno = mapa_alunos[nome_sel]
            contrato_str = data_contrato.strftime("%d/%m/%Y")
            pag_str = dt_pag.strftime("%d/%m/%Y") if dt_pag else ""
            
            # LÓGICA DO VALOR:
            # Só enviamos o valor manual SE o checkbox estiver marcado.
            # Caso contrário, enviamos None e o sistema calcula automático.
            val_final = valor_manual_input if usar_manual else None
            
            try:
                sucesso, msg = db.registrar_venda_automatica(
                    id_aluno, nome_sel, qtd_horas, "Pix", contrato_str, pag_str, valor_manual=val_final
                )
                
                if sucesso:
                    st.toast(msg, icon='✅')
                    st.cache_data.clear()
                    # st.rerun() # Opcional: força recarregamento imediato
                else:
                    st.toast(msg, icon='🚫')
            except Exception as e:
                st.toast(f"Erro: {e}", icon='🔥')
        
        if cancelar:
            # Ao clicar em cancelar, apenas recarregamos a página, o que limpa o form
            st.rerun()