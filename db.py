import gspread
import pandas as pd
from datetime import datetime
import streamlit as st
import re # Importando regex para limpar telefone

# Configuração de Conexão (Híbrida: Funciona Local e na Nuvem)
@st.cache_resource
def conectar_planilha():
    # Tenta conectar usando os Segredos do Streamlit (Nuvem)
    if "gcp_service_account" in st.secrets:
        creds_dict = st.secrets["gcp_service_account"]
        gc = gspread.service_account_from_dict(creds_dict)
    
    # Se não achar segredos, tenta conectar usando o arquivo local (Seu PC)
    else:
        try:
            gc = gspread.service_account(filename='credentials.json')
        except FileNotFoundError:
            st.error("Erro: Arquivo credentials.json não encontrado e Secrets não configurados.")
            return None

    # Substitua pelo nome EXATO da sua planilha
    sh = gc.open("DB_Education") 
    return sh

# --- FUNÇÕES DE LEITURA (GET) ---

def get_usuarios():
    sh = conectar_planilha()
    ws = sh.worksheet("CAD_Usuarios")
    return pd.DataFrame(ws.get_all_records())

def get_alunos():
    sh = conectar_planilha()
    ws = sh.worksheet("CAD_Alunos")
    df = pd.DataFrame(ws.get_all_records())
    # Filtra apenas alunos ativos para facilitar os selects
    if 'status' in df.columns:
        df = df[df['status'] == 'Ativo']
    return df

def get_professores():
    sh = conectar_planilha()
    ws = sh.worksheet("CAD_Professores")
    return pd.DataFrame(ws.get_all_records())

def get_aulas():
    sh = conectar_planilha()
    ws = sh.worksheet("MOV_Aulas")
    return pd.DataFrame(ws.get_all_records())

def get_saldo_alunos():
    """Lê a aba DASH_Dados onde estão as fórmulas de saldo"""
    sh = conectar_planilha()
    ws = sh.worksheet("DASH_Dados")
    
    # A aba DASH_Dados tem duas tabelas. Vamos pegar apenas as colunas A até F (Saldos)
    # Ajuste o range se sua tabela for maior.
    dados = ws.get("A1:F1000") 
    
    if not dados:
        return pd.DataFrame()
        
    # A primeira linha é o cabeçalho
    header = dados[1] # A linha 2 costuma ser o cabeçalho real na sua estrutura ("id_aluno", etc)
    linhas = dados[2:] # Dados a partir da linha 3
    
    return pd.DataFrame(linhas, columns=header)

# --- FUNÇÕES DE ESCRITA (POST) ---

def registrar_aula(data_aula, id_aluno, nome_aluno, id_prof, nome_prof, modalidade, duracao, obs):
    sh = conectar_planilha()
    ws = sh.worksheet("MOV_Aulas")
    
    # Gera um ID simples (pode melhorar depois)
    id_aula = len(ws.col_values(1)) + 1 
    
    # Status padrão ao criar
    status = "Realizada" 
    comissao = 0 # A fórmula do Google Sheets vai calcular isso sozinha se você configurou o ArrayFormula, 
                 # mas como usamos fórmula linha a linha, o ideal é o Python escrever 0 e você arrastar a fórmula na planilha 
                 # OU deixar em branco para o Sheets processar se tiver script.
                 # Pela sua estrutura de fórmula na célula, o Python vai sobrescrever. 
                 # Dica: Deixe o Python calcular a comissão ou use ArrayFormula na planilha.
                 # Vamos enviar "" (vazio) na comissão para tentar não quebrar, mas fórmulas arrastadas manualmentes quebram com append_row.
                 # SOLUÇÃO SEGURA: O Python escreve apenas os dados brutos. A fórmula você arrasta depois ou usa ArrayFormula na linha 2.
    
    nova_linha = [
        id_aula, 
        data_aula, # Deve ser string YYYY-MM-DD ou DD/MM/YYYY conforme sua planilha
        id_aluno,
        nome_aluno,
        id_prof,
        nome_prof,
        modalidade,
        str(duracao).replace('.', ','), # Sheets pt-BR usa vírgula
        status,
        "" # Deixa a coluna de comissão vazia para preencher/arrastar depois ou coloca 0
    ]
    
    ws.append_row(nova_linha)
    return True

# --- NOVAS FUNÇÕES DE CADASTRO (Adicione ao final do db.py) ---

def cadastrar_aluno(nome, responsavel, telefone, nascimento, serie, escola, endereco, professor, obs):
    sh = conectar_planilha()
    ws = sh.worksheet("CAD_Alunos")
    
    proximo_id = len(ws.col_values(1))
    if proximo_id == 0: proximo_id = 1
    
    # Validação e Limpeza do Telefone
    apenas_numeros = re.sub(r'\D', '', str(telefone))
    # Se tiver menos que 10 digitos, provavelmente está errado, mas salvamos o que tem
    # Se não tiver o 55, adicionamos
    if apenas_numeros:
        if not apenas_numeros.startswith('55'):
            telefone_final = f"+55{apenas_numeros}"
        else:
            telefone_final = f"+{apenas_numeros}"
    else:
        telefone_final = ""
    
    # NOVA ORDEM (Com professor inserido)
    nova_linha = [
        proximo_id,
        nome,
        responsavel,
        telefone_final,
        nascimento, 
        serie,
        escola,
        endereco,
        professor,  # <--- NOVA COLUNA AQUI
        0,          # saldo_horas
        obs,
        "Ativo"
    ]
    
    ws.append_row(nova_linha)
    return proximo_id

def cadastrar_professor(nome, val_education, val_online, val_casa):
    sh = conectar_planilha()
    ws = sh.worksheet("CAD_Professores") # Verifique se o nome da aba é CAD_Professores ou CAD_Profs
    
    proximo_id = len(ws.col_values(1))
    
    # id_prof, nome_professor, valor_hora_education, valor_hora_online, valor_hora_casa, status
    nova_linha = [
        proximo_id,
        nome,
        str(val_education).replace('.', ','),
        str(val_online).replace('.', ','),
        str(val_casa).replace('.', ','),
        "Ativo"
    ]
    
    ws.append_row(nova_linha)
    return True

def registrar_venda(id_aluno, nome_aluno, pacote, qtd_horas, valor, forma_pagamento, vencimento):
    sh = conectar_planilha()
    ws = sh.worksheet("MOV_Vendas")
    
    proximo_id = len(ws.col_values(1))
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    
    # Forçamos "Pix" se a forma_pagamento vier vazia ou diferente, mas o app já vai mandar Pix
    nova_linha = [
        proximo_id,
        data_hoje,
        id_aluno,
        nome_aluno,
        pacote,
        qtd_horas,
        str(valor).replace('.', ','),
        "Pix", # Hardcoded conforme solicitado
        str(vencimento), 
        "Pago"
    ]
    
    ws.append_row(nova_linha)
    return True
