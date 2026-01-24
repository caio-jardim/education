import streamlit as st
import pandas as pd
from datetime import date
import db 

# --- CORREÇÃO 1: ISSO PRECISA SER A PRIMEIRA COISA ---
st.set_page_config(page_title="Gestão Escolar", layout="wide", page_icon="📚")

# --- SISTEMA DE LOGIN ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['usuario'] = None

def check_login():
    st.title("🔒 Acesso ao Sistema")
    
    with st.form("login_form"):
        user = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            try:
                df_users = db.get_usuarios()
                # Verifica se a tabela veio vazia
                if df_users.empty:
                    st.error("A tabela de usuários está vazia ou não foi carregada.")
                    return

                # Converte para string para garantir comparação
                usuario_encontrado = df_users[
                    (df_users['username'].astype(str) == user) & 
                    (df_users['password'].astype(str) == password)
                ]
                
                if not usuario_encontrado.empty:
                    st.session_state['logado'] = True
                    st.session_state['usuario'] = usuario_encontrado.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
            except Exception as e:
                st.error(f"Erro ao conectar no banco: {e}")

def logout():
    st.session_state['logado'] = False
    st.session_state['usuario'] = None
    st.rerun()

# --- ÁREA DO PROFESSOR ---
def area_professor(usuario):
    st.title(f"Bem-vindo, Prof. {usuario['nome_usuario']}")
    
    tab1, tab2 = st.tabs(["📝 Lançar Aula", "📅 Meu Histórico"])
    
    # Carrega dados necessários com proteção de erro
    try:
        df_alunos = db.get_alunos()
        df_profs = db.get_professores()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return

    # Validação se as tabelas estão vazias
    if df_alunos.empty:
        st.warning("⚠️ Nenhum aluno cadastrado. Peça ao Admin para cadastrar alunos primeiro.")
        return

    if df_profs.empty:
        st.error("Erro: Tabela de professores vazia.")
        return
    
    # Pega dados do professor logado
    # Converte id_vinculo para string para garantir comparação correta com id_prof
    meus_dados = df_profs[df_profs['id_prof'].astype(str) == str(usuario['id_vinculo'])]
    
    if meus_dados.empty:
        st.error(f"Seu usuário (Vínculo {usuario['id_vinculo']}) não foi encontrado na tabela de Professores.")
        return

    nome_prof_logado = meus_dados.iloc[0]['nome_professor']
    id_prof_logado = usuario['id_vinculo']

    with tab1:
        st.subheader("Registrar Nova Aula")
        with st.form("form_aula_prof"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome_aluno_selecionado = st.selectbox("Aluno", df_alunos['nome_aluno'].unique())
                # Busca o ID do aluno selecionado de forma segura
                filtro_aluno = df_alunos[df_alunos['nome_aluno'] == nome_aluno_selecionado]
                if not filtro_aluno.empty:
                    id_aluno_sel = filtro_aluno['id_aluno'].values[0]
                else:
                    st.error("Erro ao identificar ID do aluno.")
                    st.stop()
                
                data_aula = st.date_input("Data da Aula", date.today())
                
            with col2:
                duracao = st.number_input("Duração (Horas)", min_value=0.5, step=0.5, format="%.1f")
                modalidade = st.selectbox("Modalidade", ["Education", "Online", "Casa"])
                obs = st.text_area("O que foi dado na aula?")
            
            submit = st.form_submit_button("✅ Registrar Aula")
            
            if submit:
                try:
                    data_str = data_aula.strftime("%d/%m/%Y")
                    db.registrar_aula(data_str, int(id_aluno_sel), nome_aluno_selecionado, int(id_prof_logado), nome_prof_logado, modalidade, duracao, obs)
                    st.success("Aula registrada com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

    with tab2:
        st.subheader("Minhas Aulas Realizadas")
        df_aulas = db.get_aulas()
        if not df_aulas.empty:
            # Filtra garantindo tipos iguais (str vs str ou int vs int)
            minhas_aulas = df_aulas[df_aulas['id_professor'].astype(str) == str(id_prof_logado)]
            st.dataframe(minhas_aulas)
        else:
            st.info("Nenhuma aula registrada ainda.")

# --- ÁREA DO ADMIN ---
def area_admin(usuario):
    st.title(f"Painel Administrativo - {usuario['nome_usuario']}")
    
    menu = st.sidebar.radio("Navegação", ["Visão Geral", "Cadastros & Vendas", "Financeiro Alunos", "Todas as Aulas"])
    
    if menu == "Visão Geral":
        st.info("Painel de Indicadores")
        try:
            df_saldos = db.get_saldo_alunos()
            col1, col2 = st.columns(2)
            col1.metric("Total Alunos", len(df_saldos))
        except Exception as e:
            st.error(f"Erro ao ler saldos: {e}")
        
    elif menu == "Cadastros & Vendas":
        st.subheader("Gerenciamento de Cadastros")
        
        tab1, tab2, tab3 = st.tabs(["🚀 Novo Aluno + Pacote", "💰 Venda Avulsa", "👨‍🏫 Novo Professor"])
        
        # --- ABA 1: CADASTRO COMPLETO ---
        with tab1:
            st.info("Preencha os dados. O telefone aceita apenas números (será formatado ao salvar).")
            
            # --- TÉCNICA DE CHAVE DINÂMICA (Reseta formulário sem erro) ---
            if 'reset_counter' not in st.session_state:
                st.session_state['reset_counter'] = 0
            
            # Usamos esse número no final de cada key (ex: nome_0, nome_1...)
            # Quando incrementamos o número, o Streamlit cria campos novos zerados.
            c_id = st.session_state['reset_counter']

            # Carrega lista de professores para o vínculo
            df_profs = db.get_professores()
            lista_profs = ["Selecione..."] + df_profs['nome_professor'].unique().tolist() if not df_profs.empty else ["Cadastre Professores Primeiro"]

            with st.form(key=f"form_cadastro_{c_id}"):
                st.markdown("### 1. Dados do Aluno")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    nome = st.text_input("Nome do Aluno")
                    responsavel = st.text_input("Nome do Responsável")
                    # Placeholder ensina o formato, Regex abaixo valida
                    telefone = st.text_input("Telefone (com DDD)", placeholder="61999999999")
                    
                    # AJUSTE DATA: min_value define até onde volta, max_value trava no futuro
                    nascimento = st.date_input(
                        "Data Nascimento", 
                        min_value=date(1920, 1, 1), 
                        max_value=date.today(),
                        format="DD/MM/YYYY"
                    )
                
                with col_b:
                    opcoes_series = ["Selecione...", "Infantil", "1º Ano Fund.", "2º Ano Fund.", "3º Ano Fund.", 
                                     "4º Ano Fund.", "5º Ano Fund.", "6º Ano Fund.", "7º Ano Fund.", 
                                     "8º Ano Fund.", "9º Ano Fund.", "1º Ano Ens. Médio", "2º Ano Ens. Médio", 
                                     "3º Ano Ens. Médio", "Pré-Vestibular", "Outros"]
                    serie = st.selectbox("Série/Ano", options=opcoes_series)
                    
                    # NOVO CAMPO: Professor Responsável
                    prof_resp = st.selectbox("Professor Responsável", options=lista_profs)
                    
                    escola = st.text_input("Escola de Origem")
                    endereco = st.text_input("Endereço")
                
                obs = st.text_area("Observações")
                
                st.markdown("---")
                st.markdown("### 2. Primeiro Pacote de Aulas")
                
                c1, c2, c3 = st.columns(3)
                pacote = c1.text_input("Nome do Pacote (ex: Pacote 10h)")
                qtd_horas = c2.number_input("Qtd Horas", min_value=1, step=1)
                valor = c3.number_input("Valor (R$)", min_value=0.0)
                
                c4, c5 = st.columns(2)
                # Removi o texto do Pix que você pediu para tirar
                vencimento = c5.date_input("Vencimento do Pacote", format="DD/MM/YYYY")
                
                submit_completo = st.form_submit_button("💾 Salvar Aluno e Pacote")
                
                if submit_completo:
                    # --- VALIDAÇÕES ---
                    import re
                    erros = []
                    
                    if not nome: erros.append("O Nome do Aluno é obrigatório.")
                    if prof_resp == "Selecione..." or prof_resp == "Cadastre Professores Primeiro": erros.append("Selecione um Professor Responsável.")
                    
                    # Validação de Telefone
                    # Removemos tudo que NÃO é número para checar
                    apenas_numeros = re.sub(r'\D', '', telefone)
                    if not apenas_numeros:
                        erros.append("O telefone é obrigatório e deve conter números.")
                    elif len(apenas_numeros) < 10:
                        erros.append("Telefone parece inválido (mínimo 10 dígitos com DDD).")
                    
                    if not pacote: erros.append("O Nome do Pacote é obrigatório.")

                    if erros:
                        for e in erros: st.error(e)
                    else:
                        try:
                            # Formatação e Salvamento
                            nasc_str = nascimento.strftime("%d/%m/%Y")
                            venc_str = vencimento.strftime("%d/%m/%Y")
                            
                            # Agora passamos 'prof_resp' também
                            novo_id = db.cadastrar_aluno(nome, responsavel, telefone, nasc_str, serie, escola, endereco, prof_resp, obs)
                            db.registrar_venda(novo_id, nome, pacote, qtd_horas, valor, "Pix", venc_str)
                            
                            st.success(f"✅ Aluno {nome} cadastrado com sucesso!")
                            st.toast("Dados salvos! O formulário foi limpo.", icon="✨")
                            
                            # --- A MÁGICA DA LIMPEZA ---
                            # Apenas incrementamos o contador. O Streamlit vai recriar o form com ID novo (limpo).
                            st.session_state['reset_counter'] += 1
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Erro ao salvar: {e}")

        # --- ABA 2: VENDA AVULSA ---
        with tab2:
            st.write("Adicione créditos de horas para um aluno já cadastrado.")
            df_alunos = db.get_alunos()
            
            if df_alunos.empty:
                st.warning("⚠️ Nenhum aluno cadastrado.")
            else:
                mapa_alunos = dict(zip(df_alunos['nome_aluno'], df_alunos['id_aluno']))
                
                with st.form("form_venda_avulsa"):
                    nome_sel = st.selectbox("Selecione o Aluno", df_alunos['nome_aluno'].unique())
                    
                    c1, c2, c3 = st.columns(3)
                    pacote_avulso = c1.text_input("Nome do Pacote")
                    qtd_avulsa = c2.number_input("Qtd Horas", min_value=1, step=1)
                    valor_avulso = c3.number_input("Valor (R$)", min_value=0.0)
                    
                    c4, c5 = st.columns(2)
                    venc_avulso = c5.date_input("Vencimento", format="DD/MM/YYYY")
                    
                    submit_avulso = st.form_submit_button("Registrar Venda Avulsa")
                    
                    if submit_avulso:
                        if nome_sel and pacote_avulso:
                            try:
                                id_aluno = mapa_alunos[nome_sel]
                                venc_str_avulso = venc_avulso.strftime("%d/%m/%Y")
                                db.registrar_venda(id_aluno, nome_sel, pacote_avulso, qtd_avulsa, valor_avulso, "Pix", venc_str_avulso)
                                st.success(f"Venda registrada para {nome_sel}!")
                                st.cache_data.clear()
                            except Exception as e:
                                st.error(f"Erro: {e}")
                        else:
                            st.warning("Preencha o nome do pacote.")

        # --- ABA 3: NOVO PROFESSOR ---
        with tab3:
            st.write("Cadastre um novo professor.")
            with st.form("form_novo_prof"):
                nome_prof = st.text_input("Nome do Professor")
                cp1, cp2, cp3 = st.columns(3)
                val_edu = cp1.number_input("Valor Hora (Education)", min_value=0.0)
                val_on = cp2.number_input("Valor Hora (Online)", min_value=0.0)
                val_casa = cp3.number_input("Valor Hora (Casa)", min_value=0.0)
                
                submit_prof = st.form_submit_button("Salvar Professor")
                
                if submit_prof:
                    if nome_prof:
                        try:
                            db.cadastrar_professor(nome_prof, val_edu, val_on, val_casa)
                            st.success(f"Professor {nome_prof} cadastrado!")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                    else:
                        st.warning("O nome é obrigatório.")

    elif menu == "Financeiro Alunos":
        st.subheader("Controle de Saldos")
        if st.button("🔄 Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()
        try:
            df_saldos = db.get_saldo_alunos()
            st.dataframe(df_saldos, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao carregar saldos: {e}")

    elif menu == "Todas as Aulas":
        st.subheader("Histórico Geral")
        try:
            df_aulas = db.get_aulas()
            st.dataframe(df_aulas)
        except Exception as e:
            st.error(f"Erro ao carregar aulas: {e}")

# --- CONTROLE PRINCIPAL ---
if not st.session_state['logado']:
    check_login()
else:
    with st.sidebar:
        st.write(f"Usuário: **{st.session_state['usuario']['username']}**")
        if st.button("Sair"):
            logout()
            
    if st.session_state['usuario']['tipo_perfil'] == 'admin':
        area_admin(st.session_state['usuario'])
    else:
        area_professor(st.session_state['usuario'])