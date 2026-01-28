import pandas as pd
from .connection import conectar_planilha

def get_usuarios():
    ws = conectar_planilha().worksheet("CAD_Usuarios")
    return pd.DataFrame(ws.get_all_records())

def get_alunos():
    ws = conectar_planilha().worksheet("CAD_Alunos")
    df = pd.DataFrame(ws.get_all_records())
    if 'Status' in df.columns:
        df = df[df['Status'] == 'Ativo']
    return df

def get_professores():
    ws = conectar_planilha().worksheet("CAD_Professores")
    return pd.DataFrame(ws.get_all_records())

def get_pacotes():
    ws = conectar_planilha().worksheet("CAD_Pacotes")
    return pd.DataFrame(ws.get_all_records())

def get_aulas():
    ws = conectar_planilha().worksheet("MOV_Aulas")
    return pd.DataFrame(ws.get_all_records())

def get_vinculos():
    try:
        ws = conectar_planilha().worksheet("LINK_Alunos_Professores")
        return pd.DataFrame(ws.get_all_records())
    except:
        return pd.DataFrame()

def get_financeiro_geral():
    try:
        ws = conectar_planilha().worksheet("MOV_Financeiro")
        return pd.DataFrame(ws.get_all_records())
    except:
        return pd.DataFrame()

def get_saldo_alunos():
    sh = conectar_planilha()
    ws = sh.worksheet("DASH_Dados")
    dados = ws.get_all_values()
    if len(dados) < 2: return pd.DataFrame()
    
    header = dados[1]
    linhas = dados[2:]
    df = pd.DataFrame(linhas, columns=header)
    
    colunas_desejadas = ['ID Aluno', 'Nome Aluno', 'Horas Compradas', 'Horas Consumidas', 'Horas Agendadas', 'Saldo Disponivel']
    colunas_validas = [c for c in colunas_desejadas if c in df.columns]
    
    df_limpo = df[colunas_validas].copy()
    
    if 'ID Aluno' in df_limpo.columns:
        df_limpo = df_limpo[df_limpo['ID Aluno'].astype(str).str.strip() != '']
    
    cols_num = ['Horas Compradas', 'Horas Consumidas', 'Saldo Disponivel']
    for c in cols_num:
        if c in df_limpo.columns:
            df_limpo[c] = pd.to_numeric(df_limpo[c].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

    return df_limpo