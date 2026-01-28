import streamlit as st
import database as db


def form_novo_professor():
    st.markdown("#### Cadastro de Professor")
    
    with st.form("form_prof_new", clear_on_submit=True, enter_to_submit=False):
        nome = st.text_input("Nome Completo")
        
        c1, c2, c3 = st.columns(3)
        v1 = c1.number_input("R$/h Education", min_value=0.0)
        v2 = c2.number_input("R$/h Online", min_value=0.0)
        v3 = c3.number_input("R$/h Casa", min_value=0.0)
        
        if st.form_submit_button("Salvar Professor"):
            if nome:
                db.cadastrar_professor(nome, v1, v2, v3)
                st.success(f"Professor {nome} cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("O nome é obrigatório.")